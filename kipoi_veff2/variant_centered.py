from cyvcf2 import VCF
import numpy as np
from typing import List, Iterator

import kipoi
from kipoiseq.dataclasses import Interval, Variant
from kipoiseq.extractors import VariantSeqExtractor
from kipoiseq.transforms import ReorderedOneHot
from kipoi_veff2.modelconfig import ModelConfig


class Diff:
    def __call__(self, ref_pred: List, alt_pred: List) -> List:
        return alt_pred - ref_pred


MODELS = {
    "DeepSEA/predict": ModelConfig(
        model="DeepSEA/predict",
        required_sequence_length=1000,
        transform=ReorderedOneHot(
            alphabet="ACGT", dtype=np.float32, alphabet_axis=0, dummy_axis=1
        ),
        scoring_fn=Diff(),
    )
}


def dataloader(
    vcf_file: str, fasta_file: str, sequence_length: str
) -> Iterator[tuple]:
    variant_extractor = VariantSeqExtractor(fasta_file=fasta_file)
    for cv in VCF(vcf_file):
        variant = Variant.from_cyvcf(cv)
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
