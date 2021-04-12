from pathlib import Path

from kipoi_veff2 import variant_centered


def test_modelconfig():
    test_model_config = variant_centered.MODELS["DeepSEA/predict"]
    assert test_model_config.get_model() == "DeepSEA/predict"
    assert (
        type(test_model_config.get_transform()).__name__ == "ReorderedOneHot"
    )


def test_scoring():
    test_model_config = variant_centered.MODELS["DeepSEA/predict"]
    test_dir = Path(__file__).resolve().parent
    vcf_file = str(test_dir / "data" / "singlevariant.vcf")
    fasta_file = str(test_dir / "data" / "hg38_chr22.fa")
    model_config = test_model_config
    output_file = str(test_dir / "data" / "out.vcf")
    scores = variant_centered.score_variants(
        model_config=model_config,
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        output_file=output_file,
    )
    assert len(scores) == 1
    assert scores[0].size == 919
