import csv
from typing import List, Iterator

from cyvcf2 import VCF
import numpy as np
import kipoi
from kipoiseq.dataclasses import Interval, Variant
from kipoiseq.extractors import VariantSeqExtractor
from kipoi_veff2.modelconfig import ModelConfig


class Diff:
    def __call__(self, ref_pred: List, alt_pred: List) -> List:
        return list(alt_pred - ref_pred)


MODELS = {
    "DeepSEA/predict": ModelConfig(
        model="DeepSEA/predict",
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
) -> None:
    kipoi_model = kipoi.get_model(model_config.model)
    sequence_length = model_config.get_required_sequence_length()
    transform = model_config.get_transform()
    column_labels = model_config.get_column_labels()
    with open(output_file, "w") as output_tsv:
        tsv_writer = csv.writer(output_tsv, delimiter="\t")
        tsv_writer.writerow(
            ["#CHROM", "POS", "ID", "REF", "ALT"] + column_labels
        )
        for ref, alt, variant in dataloader(
            vcf_file, fasta_file, sequence_length
        ):
            ref_prediction = kipoi_model.predict_on_batch(
                transform(ref)[np.newaxis]
            )[0]
            alt_prediction = kipoi_model.predict_on_batch(
                transform(alt)[np.newaxis]
            )[0]
            score = model_config.scoring_fn(ref_prediction, alt_prediction)
            tsv_writer.writerow(
                [
                    variant.chrom,
                    variant.pos,
                    variant.id,
                    variant.ref,
                    variant.alt,
                ]
                + score
            )
