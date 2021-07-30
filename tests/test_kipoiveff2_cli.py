from click.testing import CliRunner
from pathlib import Path
import pytest

from kipoi_veff2 import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use_variant_centered(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 0


def test_cli_correct_use_interval_based(runner, tmp_path):
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")
    output_file = str(tmp_path / "out.tsv")
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


def test_cli_correct_use_multiple_scoring_function(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.diff",
            "-s",
            "logit",
        ],
    )
    assert result.exit_code == 0


def test_cli_correct_use_different_flag(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "--model",
            "DeepSEA/predict",
            "--scoring_function",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 0


def test_cli_invalid_scoring_function(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "undefined",
        ],
    )
    assert result.exit_code == 2
    assert (
        "Removing undefined because No module named 'undefined'"
        in result.output
    )
    assert (
        "Please select atleast one available scoring function" in result.output
    )


def test_cli_undefined_scoring_function(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.abc",
        ],
    )
    assert result.exit_code == 2
    assert "'kipoi_veff2.scores' has no attribute 'abc'" in result.output
    assert (
        "Please select atleast one available scoring function" in result.output
    )


def test_cli_valid_and_invalid_scoring_function(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.logit",
            "-s",
            "undefined",
        ],
    )
    assert result.exit_code == 0


def test_cli_input_vcf_does_not_exist(runner):
    result = runner.invoke(
        cli.score_variants,
        [
            "in.vcf",
            "in.fa",
            "out.tsv",
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_VCF'" in result.output


def test_cli_missing_fasta(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(tmp_path / "out.tsv"),
            "-m",
            "DeepSEA/predict",
            "-s",
            "kipoi_veff2.scores.diff",
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
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing argument 'OUTPUT_TSV'" in result.output


def test_cli_missing_model(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing option '-m' / '--model'" in result.output


def test_cli_wrong_model(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "Dummy",
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 2
    assert "Removing Dummy as it is not supported" in result.output
    assert "Please select atleast one supported model group" in result.output


def test_cli_sequence_length(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-l",
            150,
            "-m",
            "pwm_HOCOMOCO/human/AHR",
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 0


def test_cli_no_seq_length(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(tmp_path / "out.tsv"),
            "-m",
            "pwm_HOCOMOCO/human/AHR",
            "-s",
            "kipoi_veff2.scores.diff",
        ],
    )
    assert result.exit_code == 0
