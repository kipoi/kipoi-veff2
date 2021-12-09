import csv
from dataclasses import dataclass, field
import itertools
from pathlib import Path
from typing import Any, Dict, List, Iterator, Callable, Union

from cyvcf2 import VCF
import numpy as np
import kipoi
from kipoiseq.dataclasses import Interval, Variant
from kipoiseq.extractors import VariantSeqExtractor
from kipoiseq.transforms import ReorderedOneHot

from kipoi_veff2 import scores

MODEL_GROUPS = {
    "Basset",
    "DeepBind",
    "DeepSEA",
    "MPRA-DragoNN",
    "pwm_HOCOMOCO",
    "Basenji",
}

ScoringFunction = Callable[[Any, Any], List]


@dataclass
class ModelConfig:
    """This generic class describes the available configurations for models
    whose default dataloader is kipoiseq.dataloaders.SeqIntervalDl. A sequence
    length, either chosen directly from the model description, or provided
    through the cli or provided in VARIANT_CENTERED_MODEL_GROUP_CONFIGS is
    required. A transformation function is also required to convert the
    sequences to numerical representation. By default, it is one hot
    encoded transformation. Additionally, a batch size is defined with
    a default value of 1000. This denotes number of sample that the
    model is capable of ingesting and make predictions with. Like others,
    it is also possible to override batch size through model specific
    configurations in VARIANT_CENTERED_MODEL_GROUP_CONFIGS. Finally,
    scoring funcitons must be provided for scoring the varint effect.
    By default it is scores.diff. It is also possible to over ride this in
     VARIANT_CENTERED_MODEL_GROUP_CONFIGS or a list of scoring functions
     present in kipoi_veff2.scores can be provided through cli
     using -s flag."""

    model: str
    required_sequence_length: int = None
    transform: Any = None
    batch_size: int = 1000
    default_scoring_function: Dict = field(
        default_factory=lambda: {"name": "diff", "func": scores.diff}
    )
    # This must be defined this way because dataclasses dont allow mutable
    # data type at initialization

    def __post_init__(self) -> None:
        """This function sets the model description directly"""
        self.model_description = kipoi.get_model_descr(self.model)
        self.dataloader = self.model_description.default_dataloader

    def is_sequence_model(self) -> bool:
        """This function determines whether the default dataloader is
        kipoiseq.dataloaders.SeqIntervalDl"""
        if self.dataloader.defined_as == "kipoiseq.dataloaders.SeqIntervalDl":
            return True
        else:
            return False

    def get_transform(self) -> Any:
        """A one hot encoded transformation is used as default to convert the sequences
        into numerical representation

        Raises:
            IOError: If the model's default dataloader is not
            kipoiseq.dataloaders.SeqIntervalDl

            ValueError: If there is no default transform function
        """
        if self.transform is None:
            if self.is_sequence_model():
                dataloader_args = self.dataloader.default_args
                self.transform = ReorderedOneHot(
                    alphabet="ACGT",
                    dtype=dataloader_args.get("dtype", None),
                    alphabet_axis=dataloader_args.get("alphabet_axis", 1),
                    dummy_axis=dataloader_args.get("dummy_axis", None),
                )
            else:
                raise IOError("Only supporting sequence based models for now")
        if self.transform is None:
            raise ValueError("Cannot proceed without a transform")
        else:
            return self.transform

    def get_required_sequence_length(self) -> Any:
        """
        This function returns the sequence length
        required by the model's prediction function
        """
        if self.required_sequence_length is None:
            self.required_sequence_length = self.dataloader.default_args.get(
                "auto_resize_len", None
            )
        if self.required_sequence_length is None:
            raise ValueError("Cannot proceed without required sequence length")
        else:
            return self.required_sequence_length

    def get_column_labels(
        self, scoring_functions: List[Dict[str, ScoringFunction]]
    ) -> List:
        """This function produces the header of the output tsv. The first
        five columns comprise of the information about the variant namely
        #CHROM, POS, ID, REF, ALT. The rest of the column headers are
        annotations from the model's description in kipoi if available.
        Otherwise, we use numerics in increasing order starting from 1.
        In addition, headers are also annotated with the name of the
        scoring function used

        Raises:
            IOError: If the model description is invalid
        """
        targets = self.model_description.schema.targets
        column_labels = targets.column_labels
        target_shape = targets.shape[-1]
        variant_column_labels = ["#CHROM", "POS", "ID", "REF", "ALT"]
        if column_labels:
            if len(column_labels) == target_shape:
                return variant_column_labels + [
                    f"{self.model}/{c}/{scoring_function['name']}"
                    for scoring_function in scoring_functions
                    for c in column_labels
                ]
            else:
                raise IOError(
                    "Something wrong with the model description - \
                        length of column names does not match target shape"
                )
        else:
            return variant_column_labels + [
                f"{self.model}/{num+1}/{scoring_function['name']}"
                for scoring_function in scoring_functions
                for num in range(target_shape)
            ]


def get_model_config(model_name: str, **kwargs) -> ModelConfig:
    """This function instantiates a model configuration for a
    given model"""
    # It is important to create a new dictionary for each
    # model under a model group since required sequence length
    # and transform can vary
    return ModelConfig(model=model_name, **kwargs)


VARIANT_CENTERED_MODEL_GROUP_CONFIGS = {
    "pwm_HOCOMOCO": {"required_sequence_length": 100},
    "Basenji": {
        "batch_size": 1,
        "default_scoring_function": {
            "name": "basenji_effect",
            "func": lambda ref_pred, alt_pred: (alt_pred - ref_pred).mean(
                axis=0
            )[np.newaxis, :],
        },
    },
}


def batcher(iterable, batch_size) -> List:
    """This function returns a list of elements
    of length batch_size from an iterable"""
    while True:
        batch = list(itertools.islice(iterable, batch_size))
        if not batch:
            break
        yield batch


def batch_dataloader(
    vcf_file: str, fasta_file: str, sequence_length: str, batch_size: int
) -> Iterator[tuple]:
    """This extracts a batch of variants of size batch_size from the input
    vcf file. For each such variant a reference sequence is extracted from
    the fasta file centered on the said variant. An alternative sequence is
    also extracted where the central base is mutated according the alternative
    allele of the variant. Finally a tuple containing the list of reference
    sequences, list of alternative sequences and list of variants - all
    of length batch_size are returned."""
    variant_extractor = VariantSeqExtractor(fasta_file=fasta_file)
    for cvs in batcher(VCF(vcf_file), batch_size):
        variants = [Variant.from_cyvcf(cv) for cv in cvs]
        intervals = [
            Interval(variant.chrom, variant.pos - 1, variant.pos).resize(
                sequence_length
            )
            for variant in variants
        ]
        refs = [
            variant_extractor.extract(
                interval, variants=[], anchor=sequence_length
            )
            for interval in intervals
        ]
        alts = [
            variant_extractor.extract(
                interval, variants=[variants[index]], anchor=interval.center()
            )
            for index, interval in enumerate(intervals)
        ]
        yield (refs, alts, variants)


def score_variants(
    model_config: ModelConfig,
    vcf_file: str,
    fasta_file: str,
    output_file: Union[str, Path],
    scoring_functions: List[Dict[str, ScoringFunction]] = [],
) -> None:
    """This function perfoms variant effect prediction for sequence
    based models. The steps are as follows
    1. A kipoi model object is instantiated that will give access to
    the model's predict_on_batch function
    2. The input vcf file is iterated in batches and data consisting
    of the reference, alternative sequences and variants are prepared
    for the model to infer with.
    3. The model performs inference with both the reference and
    alternative sequences.
    4. Effects are scored with the desired scoring functions using
    the reference and alternative predictions.
    5. Finally, the scored effects and variants used to generate
    the effects are written to a tsv file.
    """
    kipoi_model = kipoi.get_model(model_config.model)
    sequence_length = model_config.get_required_sequence_length()
    transform = model_config.get_transform()
    if not scoring_functions:
        # If no scoring function is provided through cli, fall back
        # on the default scoring function for the model
        scoring_functions = [model_config.default_scoring_function]
    column_labels = model_config.get_column_labels(
        scoring_functions=scoring_functions
    )
    with open(output_file, "w") as output_tsv:
        tsv_writer = csv.writer(output_tsv, delimiter="\t")
        tsv_writer.writerow(column_labels)

        for refs, alts, variants in batch_dataloader(
            vcf_file, fasta_file, sequence_length, model_config.batch_size
        ):
            if model_config.batch_size == 1:
                ref_batch = transform(refs[0])[np.newaxis]
                alt_batch = transform(alts[0])[np.newaxis]
                ref_alt_batch = np.concatenate((ref_batch, alt_batch), axis=0)
                ref_alt_prediction = kipoi_model.predict_on_batch(
                    ref_alt_batch
                )
                ref_predictions, alt_predictions = (
                    ref_alt_prediction[0],
                    ref_alt_prediction[1],
                )
            else:
                refs = np.stack([transform(ref) for ref in refs], axis=0)
                ref_predictions = kipoi_model.predict_on_batch(refs)
                alts = np.stack([transform(alt) for alt in alts], axis=0)
                alt_predictions = kipoi_model.predict_on_batch(alts)

            aggregated_scores = scoring_functions[0]["func"](
                ref_predictions, alt_predictions
            )
            if aggregated_scores.ndim == 0:
                aggregated_scores = aggregated_scores[np.newaxis]
            if aggregated_scores.ndim == 1:
                aggregated_scores = aggregated_scores[:, np.newaxis]
            for scoring_function in scoring_functions[1:]:
                scores = scoring_function["func"](
                    ref_predictions, alt_predictions
                )
                if scores.ndim == 0:
                    scores = scores[np.newaxis]
                if scores.ndim == 1:
                    scores = scores[:, np.newaxis]

                aggregated_scores = np.concatenate(
                    (
                        aggregated_scores,
                        scores,
                    ),
                    axis=1,
                )

            for index, variant in enumerate(variants):
                tsv_writer.writerow(
                    [
                        variant.chrom,
                        variant.pos,
                        variant.id,
                        variant.ref,
                        variant.alt,
                    ]
                    + (
                        [aggregated_scores[index]]
                        if np.isscalar(aggregated_scores[index])
                        else list(aggregated_scores[index])
                    )
                )
