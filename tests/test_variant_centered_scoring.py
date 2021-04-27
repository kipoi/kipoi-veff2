import csv
from pathlib import Path

from kipoi_veff2 import variant_centered
from kipoi_veff2 import scores

import pytest


def test_variant_centered_modelconfig():
    test_model_config = variant_centered.get_model_config("DeepSEA/predict")
    assert test_model_config.get_model() == "DeepSEA/predict"
    assert test_model_config.get_required_sequence_length() == 1000
    assert (
        type(test_model_config.get_transform()).__name__ == "ReorderedOneHot"
    )
    assert test_model_config.get_transform().dtype.__name__ == "float32"
    assert test_model_config.get_transform().alphabet_axis == 0
    assert test_model_config.get_transform().dummy_axis == 1
    assert test_model_config.get_transform().alphabet == ["A", "C", "G", "T"]


@pytest.mark.parametrize(
    "model_name, header_name, number_of_headers",
    [
        ("Basset", "Basset/PANC/diff", 169),
        (
            "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF",
            "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF/1/diff",
            6,
        ),
        (
            "DeepSEA/beluga",
            "DeepSEA/beluga/Osteoblasts_H4K20me1_None/diff",
            2007,
        ),
        (
            "DeepSEA/predict",
            "DeepSEA/predict/Osteoblasts_H3K9me3_None/diff",
            924,
        ),
        (
            "DeepSEA/variantEffects",
            "DeepSEA/variantEffects/Osteoblasts_H3K9me3_None/diff",
            924,
        ),
    ],
)
def test_variant_centered_scoring_single_scoring_function(
    model_name, header_name, number_of_headers
):
    test_model_config = variant_centered.get_model_config(model_name)
    assert test_model_config.get_model() == model_name
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = test_dir / "data" / f"out.{model_name.replace('/', '_')}.tsv"

    variant_centered.score_variants(
        model_config=model_config,
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        output_file=output_file,
        scoring_functions=[{"name": "diff", "func": scores.diff}],
    )
    assert output_file.exists()
    with open(output_file, "r") as output_file_handle:
        tsv_reader = csv.reader(output_file_handle, delimiter="\t")
        header = next(tsv_reader)
        assert len(header) == number_of_headers
        assert header[number_of_headers - 1] == header_name
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers
    output_file.unlink()


@pytest.mark.parametrize(
    "model_name, diff_header_name, logit_header_name, number_of_headers",
    [
        ("Basset", "Basset/8988T/diff", "Basset/PANC/logit", 333),
        (
            "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF",
            "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF/1/diff",
            "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF/1/logit",
            7,
        ),
        (
            "DeepSEA/beluga",
            "DeepSEA/beluga/8988T_DNase_None/diff",
            "DeepSEA/beluga/Osteoblasts_H4K20me1_None/logit",
            4009,
        ),
        (
            "DeepSEA/predict",
            "DeepSEA/predict/8988T_DNase_None/diff",
            "DeepSEA/predict/Osteoblasts_H3K9me3_None/logit",
            1843,
        ),
        (
            "DeepSEA/variantEffects",
            "DeepSEA/variantEffects/8988T_DNase_None/diff",
            "DeepSEA/variantEffects/Osteoblasts_H3K9me3_None/logit",
            1843,
        ),
    ],
)
def test_variant_centered_scoring_multiple_scoring_functions(
    model_name, diff_header_name, logit_header_name, number_of_headers
):
    test_model_config = variant_centered.get_model_config(model_name)
    assert test_model_config.get_model() == model_name
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = Path(
        test_dir / "data" / f"out.{model_name.replace('/', '_')}.tsv"
    )

    variant_centered.score_variants(
        model_config=model_config,
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        output_file=output_file,
        scoring_functions=[
            {"name": "diff", "func": scores.diff},
            {"name": "logit", "func": scores.logit},
        ],
    )
    assert output_file.exists()
    with open(output_file, "r") as output_file_handle:
        tsv_reader = csv.reader(output_file_handle, delimiter="\t")
        header = next(tsv_reader)
        assert len(header) == number_of_headers
        assert header[5] == diff_header_name
        assert header[number_of_headers - 1] == logit_header_name
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers
    output_file.unlink()
