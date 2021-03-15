from click.testing import CliRunner
from pathlib import Path
import pytest

from kipoi_veff2 import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use_single_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [str(test_dir / "dummy.vcf"), "out.vcf", "-m", "Basset"],
    )
    assert result.exit_code == 0
    assert "models=['Basset']" in result.output


def test_cli_correct_use_single_model_diff_flag(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [str(test_dir / "dummy.vcf"), "out.vcf", "--models", "Basset"],
    )
    assert result.exit_code == 0
    assert "models=['Basset']" in result.output


def test_cli_correct_use_multiple_models(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "dummy.vcf"),
            "out.vcf",
            "-m",
            "Basset",
            "-m",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 0
    assert "models=['Basset', 'DeepSEA/predict']" in result.output


def test_cli_correct_use_multiple_models_wrong_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "dummy.vcf"),
            "out.vcf",
            "-m",
            "DeepBind/Gallus_gallus/RBP/D00278.001_RNAcompete_RBM47",
            "-m",
            "Dummy",
        ],
    )
    assert result.exit_code == 0
    assert "Removing Dummy as it is not supported" in result.output
    assert (
        "models=['DeepBind/Gallus_gallus/RBP/D00278.001_RNAcompete_RBM47']"
        in result.output
    )
    assert (
        "models=\
        ['DeepBind/Gallus_gallus/RBP/D00278.001_RNAcompete_RBM47', 'Dummy']"
        not in result.output
    )


def test_cli_input_file_does_not_exist(runner):
    result = runner.invoke(
        cli.score_variants, ["in.vcf", "out.vcf", "-m", "Basset"]
    )
    assert result.exit_code == 2
    assert "Error: Invalid value" in result.output


def test_cli_missing_output(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants, [str(test_dir / "dummy.vcf"), "-m", "Basset"]
    )
    assert result.exit_code == 2
    assert "Error: Missing argument" in result.output


def test_cli_missing_models(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants, [str(test_dir / "dummy.vcf"), "out.vcf"]
    )
    assert result.exit_code == 2
    assert "Error: Missing option" in result.output


def test_cli_wrong_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [str(test_dir / "dummy.vcf"), "out.vcf", "-m", "Dummy"],
    )
    assert result.exit_code == 2
    assert "Removing Dummy as it is not supported" in result.output
    assert "Please select atleast one supported model group" in result.output
