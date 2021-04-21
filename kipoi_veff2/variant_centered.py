import csv
from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import Any, Dict, List, Iterator, Callable, Union

from cyvcf2 import VCF
import numpy as np
import kipoi
from kipoiseq.dataclasses import Interval, Variant
from kipoiseq.extractors import VariantSeqExtractor
from kipoiseq.transforms import ReorderedOneHot

MODELGROUPS = ["Basset", "DeepBind", "DeepSEA"]


@dataclass
class ModelConfig:
    model: str
    required_sequence_length: int = None
    transform: Any = None

    def __post_init__(self):
        self.model_description = kipoi.get_model_descr(self.model)
        self.dataloader = self.model_description.default_dataloader

    def is_sequence_model(self) -> bool:
        if self.dataloader.defined_as == "kipoiseq.dataloaders.SeqIntervalDl":
            return True
        else:
            return False

    def get_model(self) -> str:
        return self.model

    def get_transform(self) -> Any:
        if self.transform is None:
            if self.is_sequence_model():
                dataloader_args = self.dataloader.default_args
                self.transform = ReorderedOneHot(
                    alphabet="ACGT",
                    dtype=dataloader_args["dtype"]
                    if "dtype" in dataloader_args
                    else None,
                    alphabet_axis=dataloader_args["alphabet_axis"]
                    if "alphabet_axis" in dataloader_args
                    else 1,
                    dummy_axis=dataloader_args["dummy_axis"]
                    if "dummy_axis" in dataloader_args
                    else None,
                )
            else:
                raise IOError("Only supporting sequence based models for now")
        if self.transform is None:
            raise ValueError("Cannot proceed without a transform")
        else:
            return self.transform

    def get_required_sequence_length(self) -> Any:
        if self.required_sequence_length is None:
            self.required_sequence_length = self.dataloader.default_args.get(
                "auto_resize_len", None
            )
        if self.required_sequence_length is None:
            raise ValueError("Cannot proceed without required sequence length")
        else:
            return self.required_sequence_length

    def get_column_labels(
        self, list_of_scoring_fn: List[Dict[str, Callable[[Any, Any], List]]]
    ) -> List:
        targets = self.model_description.schema.targets
        column_labels = targets.column_labels
        target_shape = targets.shape[0]
        variant_column_labels = ["#CHROM", "POS", "ID", "REF", "ALT"]
        if column_labels:
            if len(column_labels) == target_shape:
                return variant_column_labels + [
                    f"{self.model}/{c}/{scoring_fn['name']}"
                    for scoring_fn in list_of_scoring_fn
                    for c in column_labels
                ]
            else:
                raise IOError(
                    "Something wrong with the model description - \
                        length of column names does not match target shape"
                )
        else:
            return variant_column_labels + [
                f"{self.model}/{num+1}/{scoring_fn['name']}"
                for scoring_fn in list_of_scoring_fn
                for num in range(target_shape)
            ]


def get_model_config(model_name: str) -> ModelConfig:
    return ModelConfig(model=model_name)


def dataloader(
    vcf_file: str, fasta_file: str, sequence_length: str
) -> Iterator[tuple]:
    variant_extractor = VariantSeqExtractor(fasta_file=fasta_file)
    for cv in VCF(vcf_file):
        variant = Variant.from_cyvcf(cv)
        # Interval centered at the variant
        interval = Interval(
            variant.chrom, variant.pos - 1, variant.pos
        ).resize(sequence_length)
        ref = variant_extractor.extract(
            interval, variants=[], anchor=sequence_length
        )
        alt = variant_extractor.extract(
            interval, variants=[variant], anchor=interval.center()
        )
        yield (ref, alt, variant)


def score_variants(
    model_config: ModelConfig,
    vcf_file: str,
    fasta_file: str,
    output_file: Union[str, Path],
    list_of_scoring_fn: List[Dict[str, Callable[[Any, Any], List]]],
) -> None:
    kipoi_model = kipoi.get_model(model_config.model)
    sequence_length = model_config.get_required_sequence_length()
    transform = model_config.get_transform()
    column_labels = model_config.get_column_labels(
        list_of_scoring_fn=list_of_scoring_fn
    )
    with open(output_file, "w") as output_tsv:
        tsv_writer = csv.writer(output_tsv, delimiter="\t")
        tsv_writer.writerow(column_labels)
        for ref, alt, variant in dataloader(
            vcf_file, fasta_file, sequence_length
        ):
            ref_prediction = kipoi_model.predict_on_batch(
                transform(ref)[np.newaxis]
            )[0]
            alt_prediction = kipoi_model.predict_on_batch(
                transform(alt)[np.newaxis]
            )[0]
            scores = [
                scoring_fn["func"](ref_prediction, alt_prediction)
                for scoring_fn in list_of_scoring_fn
            ]
            scores = list(itertools.chain.from_iterable(scores))
            tsv_writer.writerow(
                [
                    variant.chrom,
                    variant.pos,
                    variant.id,
                    variant.ref,
                    variant.alt,
                ]
                + scores
            )
