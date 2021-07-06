import csv
from pathlib import Path

from kipoi_veff2 import variant_centered
from kipoi_veff2 import scores

import pytest


def test_variant_centered_modelconfig():
    test_model_config = variant_centered.get_model_config("Divergent421")
    assert test_model_config.model == "Divergent421"
    assert test_model_config.get_required_sequence_length() == 1000
    assert (
        type(test_model_config.get_transform()).__name__ == "ReorderedOneHot"
    )


@pytest.mark.parametrize(
    "model_name, header_name, number_of_headers",
    [
        ("Divergent421", "Divergent421/ENCSR979BPU/diff", 426),
        (
            "CpGenie/U_87_MG_ENCSR000DDQ",
            "CpGenie/U_87_MG_ENCSR000DDQ/unmethylation_prob/diff",
            7,
        ),
    ],
)
def test_variant_centered_scoring_single_scoring_function(
    model_name, header_name, number_of_headers, tmp_path
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
        assert header[number_of_headers - 1] == header_name
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers


@pytest.mark.parametrize(
    "model_name, diff_header_name, logit_header_name, number_of_headers",
    [
        (
            "Divergent421",
            "Divergent421/ENCSR000EID/diff",
            "Divergent421/ENCSR979BPU/logit",
            847,
        ),
        (
            "CpGenie/U_87_MG_ENCSR000DDQ",
            "CpGenie/U_87_MG_ENCSR000DDQ/methylation_prob/diff",
            "CpGenie/U_87_MG_ENCSR000DDQ/unmethylation_prob/logit",
            9,
        ),
    ],
)
def test_variant_centered_scoring_multiple_scoring_functions(
    model_name,
    diff_header_name,
    logit_header_name,
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
        assert header[5] == diff_header_name
        assert header[number_of_headers - 1] == logit_header_name
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers
