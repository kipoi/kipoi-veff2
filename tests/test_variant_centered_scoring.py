import csv
from pathlib import Path

from kipoi_veff2 import variant_centered
from kipoi_veff2 import scores

import pytest


def test_variant_centered_modelconfig_batchsize():
    test_model_config_dict = (
        variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
            "Basenji", {}
        )
    )
    test_model_config = variant_centered.get_model_config(
        "Basenji", **test_model_config_dict
    )
    assert test_model_config.model == "Basenji"
    assert test_model_config.batch_size == 1


def test_variant_centered_modelconfig():
    test_model_config_dict = (
        variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
            "DeepSEA/predict", {}
        )
    )
    test_model_config = variant_centered.get_model_config(
        "DeepSEA/predict", **test_model_config_dict
    )
    assert test_model_config.model == "DeepSEA/predict"
    assert test_model_config.batch_size == 32
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
        ("Basenji", "Basenji/4229/basenji_effect", 4234),
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
        (
            "MPRA-DragoNN/ConvModel",
            "MPRA-DragoNN/ConvModel/12/diff",
            17,
        ),
        (
            "MPRA-DragoNN/DeepFactorizedModel",
            "MPRA-DragoNN/DeepFactorizedModel/12/diff",
            17,
        ),
        (
            "pwm_HOCOMOCO/human/AHR",
            "pwm_HOCOMOCO/human/AHR/1/diff",
            6,
        ),
    ],
)
def test_variant_centered_scoring_single_scoring_function(
    model_name, header_name, number_of_headers, tmp_path
):
    model_group = model_name.split("/")[0]
    model_group_config_dict = (
        variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
            model_group, {}
        )
    )
    test_model_config = variant_centered.get_model_config(
        model_name, **model_group_config_dict
    )
    assert test_model_config.model == model_name
    for attr_name, attr_val in model_group_config_dict.items():
        assert getattr(test_model_config, attr_name) == attr_val
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
        (
            "MPRA-DragoNN/ConvModel",
            "MPRA-DragoNN/ConvModel/1/diff",
            "MPRA-DragoNN/ConvModel/12/logit",
            29,
        ),
        (
            "MPRA-DragoNN/DeepFactorizedModel",
            "MPRA-DragoNN/DeepFactorizedModel/1/diff",
            "MPRA-DragoNN/DeepFactorizedModel/12/logit",
            29,
        ),
        (
            "pwm_HOCOMOCO/human/AHR",
            "pwm_HOCOMOCO/human/AHR/1/diff",
            "pwm_HOCOMOCO/human/AHR/1/logit",
            7,
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
    model_group = model_name.split("/")[0]
    model_group_config_dict = (
        variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
            model_group, {}
        )
    )
    test_model_config = variant_centered.get_model_config(
        model_name, **model_group_config_dict
    )
    assert test_model_config.model == model_name
    for attr_name, attr_val in model_group_config_dict.items():
        assert getattr(test_model_config, attr_name) == attr_val
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
