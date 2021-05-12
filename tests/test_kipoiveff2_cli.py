from click.testing import CliRunner
from pathlib import Path
import pytest

from kipoi_veff2 import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use_variant_centered(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "diff",
        ],
    )
    assert result.exit_code == 0
    Path(test_dir / "data" / "general" / "out.tsv").unlink()


def test_cli_correct_use_interval_based(runner):
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")
    output_file = str(interval_based_test_dir / "out.tsv")
    result = runner.invoke(
        cli.score_variants,
        [
            vcf_file,
            fasta_file,
            "-g",
            gtf_file,
            output_file,
            "-m",
            "MMSplice/modularPredictions",
        ],
    )
    assert result.exit_code == 0


def test_cli_correct_use_multiple_scoring_function(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "diff",
            "-s",
            "logit",
        ],
    )
    assert result.exit_code == 0
    Path(test_dir / "data" / "general" / "out.tsv").unlink()


def test_cli_correct_use_different_flag(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "--model",
            "DeepSEA/predict",
            "--scoring_function",
            "diff",
        ],
    )
    assert result.exit_code == 0
    Path(test_dir / "data" / "general" / "out.tsv").unlink()


def test_cli_invalid_scoring_function(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "undefined",
        ],
    )
    assert result.exit_code == 2
    assert (
        "Please select atleast one available scoring function" in result.output
    )


def test_cli_valid_and_invalid_scoring_function(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "logit",
            "-s",
            "undefined",
        ],
    )
    assert result.exit_code == 0
    Path(test_dir / "data" / "general" / "out.tsv").unlink()


def test_cli_input_vcf_does_not_exist(runner):
    result = runner.invoke(
        cli.score_variants,
        ["in.vcf", "in.fa", "out.tsv", "-m", "DeepSEA/predict", "-s", "diff"],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_VCF'" in result.output


def test_cli_missing_fasta(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_FASTA'" in result.output


def test_cli_missing_output(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing argument 'OUTPUT_TSV'" in result.output


def test_cli_missing_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-s",
            "diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing option '-m' / '--model'" in result.output


def test_cli_wrong_model(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(test_dir / "data" / "general" / "out.tsv"),
            "-m",
            "Dummy",
            "-s",
            "diff",
        ],
    )
    assert result.exit_code == 2
    assert "Removing Dummy as it is not supported" in result.output
    assert "Please select atleast one supported model group" in result.output
