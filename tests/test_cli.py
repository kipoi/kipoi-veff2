from click.testing import CliRunner
from pathlib import Path
import pytest

from kipoi_veff2 import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            "out.vcf",
            "-m",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 0
    assert "model=DeepSEA/predict" in result.output


def test_cli_correct_use_single_model_diff_flag(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            "out.vcf",
            "--model",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 0
    assert "model=DeepSEA/predict" in result.output


def test_cli_input_vcf_does_not_exist(runner):
    result = runner.invoke(
        cli.score_variants,
        ["in.vcf", "in.fa", "out.vcf", "-m", "DeepSEA/predict"],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_VCF'" in result.output


def test_cli_missing_fasta(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            "out.vcf",
            "-m",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_FASTA'" in result.output


def test_cli_missing_output(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            "-m",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing argument 'OUTPUT_VCF'" in result.output


def test_cli_missing_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            "out.vcf",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing option '-m' / '--model'" in result.output


def test_cli_wrong_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            "out.vcf",
            "-m",
            "Dummy",
        ],
    )
    assert result.exit_code == 2
    assert "Removing Dummy as it is not supported" in result.output
    assert "Please select atleast one supported model group" in result.output
