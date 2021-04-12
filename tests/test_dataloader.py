from pathlib import Path

from kipoiseq.dataclasses import Variant
from kipoi_veff2 import variant_centered


def test_dataloader():
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "hg38_chr22.fa")
    sequence_length = 10

    for ref, alt, variant in variant_centered.dataloader(
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        sequence_length=sequence_length,
    ):
        assert ref == "TGGTGATTTT"
        assert alt == "TGGTTATTTT"
        assert variant == Variant(
            chrom="chr22", pos=21541590, ref="A", alt="T", id="None"
        )
