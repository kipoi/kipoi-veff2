from dataclasses import dataclass
from typing import Any, Callable, List, Iterator

from cyvcf2 import VCF
import numpy as np
import kipoi
from kipoiseq.dataclasses import Interval, Variant
from kipoiseq.extractors import VariantSeqExtractor
from kipoiseq.transforms import ReorderedOneHot


@dataclass
class ModelConfig:
    model: str
    scoring_fn: Callable[[List, List], List]
    required_sequence_length: int = None
    transform: Any = None

    def __post_init__(self):
        self.model_description = kipoi.get_model_descr(self.model)
        self.dataloader = self.model_description.default_dataloader

    def get_model(self) -> str:
        return self.model

    def get_transform(self) -> Any:
        if self.transform is None:
            # Infer from the model. raise an error if you cannot find them
            pass
        return self.transform


def diff(ref_pred: List, alt_pred: List) -> List:
    return alt_pred - ref_pred


MODELS = {
    "Basset": ModelConfig(
        model="Basset",
        scoring_fn=diff,
    ),
    "DeepSEA/beluga": ModelConfig(
        model="DeepSEA/beluga",
        scoring_fn=diff,
    ),
    "DeepSEA/predict": ModelConfig(
        model="DeepSEA/predict",
        scoring_fn=diff,
    ),
    "DeepSEA/variantEffects": ModelConfig(
        model="DeepSEA/variantEffects",
        scoring_fn=diff,
    ),
}


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
    model_config: ModelConfig, vcf_file: str, fasta_file: str, output_file: str
) -> List:
    kipoi_model = kipoi.get_model(model_config.model)
    sequence_length = model_config.required_sequence_length
    transform = model_config.get_transform()
    scores = []
    for ref, alt, variant in dataloader(vcf_file, fasta_file, sequence_length):
        ref_prediction = kipoi_model.predict_on_batch(
            transform(ref)[np.newaxis]
        )[0]
        alt_prediction = kipoi_model.predict_on_batch(
            transform(alt)[np.newaxis]
        )[0]
        score = model_config.scoring_fn(ref_prediction, alt_prediction)
        scores.append(score)
    return scores
