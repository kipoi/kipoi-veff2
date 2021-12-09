from pathlib import Path
import pytest

from kipoiseq.dataclasses import Variant
from kipoi_veff2 import variant_centered
from kipoi_veff2 import interval_based


def test_variant_cenetered_dataloader():
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "general" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "general" / "hg38_chr22.fa")
    sequence_length = 10

    for ref, alt, variant in variant_centered.batch_dataloader(
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        sequence_length=sequence_length,
        batch_size=1,
    ):
        assert ref == ["TGGTGATTTT"]
        assert alt == ["TGGTTATTTT"]
        assert variant == [
            Variant(chrom="chr22", pos=21541590, ref="A", alt="T", id="None")
        ]


def test_variant_cenetered_dataloader_bigger_batch_size():
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "general" / "test.vcf")
    fasta_file = str(test_dir / "data" / "general" / "hg38_chr22.fa")
    sequence_length = 10

    for refs, alts, variants in variant_centered.batch_dataloader(
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        sequence_length=sequence_length,
        batch_size=20,
    ):
        assert refs == [
            "TGGTGATTTT",
            "CTGTGCTCAA",
            "CACCAAGGCC",
            "CACCAAGGCC",
            "CACCAAGGCC",
            "CACCAAGGCC",
            "TTATTTATTT",
            "ATCTTTATTT",
            "TGAGGATGTT",
        ]
        assert alts == [
            "TGGTTATTTT",
            "CTGTCCTCAA",
            "CACCGAGGCC",
            "CACCGGCCTG",
            "CCACCAGGCC",
            "CACCGAGGCC",
            "TTATGTATTT",
            "ATCTATATTT",
            "TGAGAATGTT",
        ]
        assert variants[0] == Variant(
            chrom="chr22", pos=21541590, ref="A", alt="T", id="None"
        )


def test_interval_based_dataloader_missing_parameter():
    test_model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[
        "MMSplice/deltaLogitPSI"
    ]
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    gtf_file = str(interval_based_test_dir / "test.gtf")

    with pytest.raises(Exception) as error_msg:
        test_model_config.get_dataloader(
            {
                "gtf_file": gtf_file,
                "vcf_file": vcf_file,
            }
        )
    assert (
        str(error_msg.value)
        == "The dataloader is missing one or more required arguments"
    )


def test_interval_based_dataloader_wrong_parameter():
    test_model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[
        "MMSplice/deltaLogitPSI"
    ]
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")

    with pytest.raises(Exception) as error_msg:
        test_model_config.get_dataloader(
            {
                "fasta": fasta_file,
                "gtf_file": gtf_file,
                "vcf_file": vcf_file,
            }
        )
    assert (
        str(error_msg.value)
        == "The dataloader is missing one or more required arguments"
    )


def test_interval_based_dataloader():
    test_model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[
        "MMSplice/pathogenicity"
    ]
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")
    dataloader = test_model_config.get_dataloader(
        {
            "fasta_file": fasta_file,
            "gtf_file": gtf_file,
            "vcf_file": vcf_file,
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
