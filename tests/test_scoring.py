import csv
from pathlib import Path

from kipoi_veff2 import variant_centered
import pytest


def test_modelconfig():
    test_model_config = variant_centered.MODELS["DeepSEA/predict"]
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
        ("Basset", "Basset/PANC", 169),
        ("DeepSEA/beluga", "DeepSEA/beluga/Osteoblasts_H4K20me1_None", 2007),
        ("DeepSEA/predict", "DeepSEA/predict/Osteoblasts_H3K9me3_None", 924),
        (
            "DeepSEA/variantEffects",
            "DeepSEA/variantEffects/Osteoblasts_H3K9me3_None",
            924,
        ),
    ],
)
def test_scoring(model_name, header_name, number_of_headers):
    test_model_config = variant_centered.MODELS[model_name]
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = str(test_dir / "data" / "out.tsv")
    variant_centered.score_variants(
        model_config=model_config,
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        output_file=output_file,
    )
    assert Path(output_file).exists()
    with open(output_file, "r") as output_file_handle:
        tsv_reader = csv.reader(output_file_handle, delimiter="\t")
        header = next(tsv_reader)
        assert len(header) == number_of_headers
        assert header[number_of_headers - 1] == header_name
        row = next(tsv_reader)
        assert row[2] == ""
        assert len(row) == number_of_headers
