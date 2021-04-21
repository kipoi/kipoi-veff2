from pathlib import Path

from kipoiseq.dataclasses import Variant
from kipoi_veff2 import variant_centered
from kipoi_veff2 import interval_based


def test_variant_cenetered_dataloader():
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


def test_interval_based_dataloader():
    test_model_config = interval_based.get_model_config(
        "MMSplice/pathogenicity"
    )
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")
    dataloader = test_model_config.get_dataloader(
        {
            "fasta": fasta_file,
            "gtf": gtf_file,
            "vcf": vcf_file,
        }
    )
    batch = next(dataloader)
    assert sorted(list(batch.keys())) == ["inputs", "metadata"]
    assert sorted(list(batch["inputs"].keys())) == ["mut_seq", "seq"]
    assert sorted(list(batch["inputs"]["seq"].keys())) == sorted(
        list(batch["inputs"]["mut_seq"].keys())
    )
    assert sorted(list(batch["metadata"].keys())) == ["exon", "variant"]
    assert sorted(list(batch["metadata"]["variant"].keys())) == [
        "alt",
        "annotation",
        "chrom",
        "pos",
        "ref",
    ]
    assert "exon_id" in batch["metadata"]["exon"].keys()
    annotation_id = batch["metadata"]["variant"]["annotation"]
    exon_id = batch["metadata"]["exon"]["exon_id"]
    assert (
        f"{annotation_id}:{exon_id}"
        == "17:41197805:ACATCTGCC>A:ENSE00001814242"
    )
