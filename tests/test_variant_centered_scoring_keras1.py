import csv
from pathlib import Path

from kipoi_veff2 import variant_centered
from kipoi_veff2 import scores

import pytest


def test_variant_centered_modelconfig_keras1():
    test_model_config = variant_centered.get_model_config("Divergent421")
    assert test_model_config.model == "Divergent421"
    assert test_model_config.get_required_sequence_length() == 1000
    assert (
        type(test_model_config.get_transform()).__name__ == "ReorderedOneHot"
    )


@pytest.mark.parametrize(
    "model_name, number_of_headers",
    [
        ("Divergent421", 426),
        ("CpGenie/U_87_MG_ENCSR000DDQ", 7),
    ],
)
def test_variant_centered_scoring_single_scoring_function_keras1(
    model_name, number_of_headers, tmp_path
):
    test_model_config = variant_centered.get_model_config(model_name)
    assert test_model_config.model == model_name
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "general" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "general" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = tmp_path / f"out.{model_name.replace('/', '_')}.tsv"

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
        assert header[number_of_headers - 1].split("/")[-1] == "diff"
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers


@pytest.mark.parametrize(
    "model_name, number_of_headers",
    [
        ("Divergent421", 847),
        ("CpGenie/U_87_MG_ENCSR000DDQ", 9),
    ],
)
def test_variant_centered_scoring_multiple_scoring_functions_keras1(
    model_name,
    number_of_headers,
    tmp_path,
):
    test_model_config = variant_centered.get_model_config(model_name)
    assert test_model_config.model == model_name
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "general" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "general" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = tmp_path / f"out.{model_name.replace('/', '_')}.tsv"

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
        assert header[5].split("/")[-1] == "diff"
        assert header[number_of_headers - 1].split("/")[-1] == "logit"
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers
