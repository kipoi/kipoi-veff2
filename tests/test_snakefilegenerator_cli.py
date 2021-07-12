from click.testing import CliRunner
from pathlib import Path
import pytest

from kipoi_veff2 import snakefilegenerator


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    output_dir.mkdir()
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "-mg",
            "DeepSEA",
            "-mg",
            "Basset",
            "-n",
            "2",
        ],
    )
    assert result.exit_code == 0
    assert (output_dir / "Snakefile.0").exists()
    assert (output_dir / "Snakefile.1").exists()
    with open(output_dir / "Snakefile.0", "r") as snakefile_handle:
        lines = snakefile_handle.readlines()

    assert (
        lines[6] == "models = ['DeepSEA/variantEffects', 'DeepSEA/beluga']\n"
    )

    with open(output_dir / "Snakefile.1", "r") as snakefile_handle:
        lines = snakefile_handle.readlines()

    assert lines[6] == "models = ['DeepSEA/predict', 'Basset']\n"


def test_cli_correct_use_different_flag(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    output_dir.mkdir()
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "--model-groups",
            "DeepSEA",
            "--model-groups",
            "Basset",
            "--number-of-shards",
            "2",
        ],
    )
    assert result.exit_code == 0
    assert (output_dir / "Snakefile.0").exists()
    assert (output_dir / "Snakefile.1").exists()
    with open(output_dir / "Snakefile.0", "r") as snakefile_handle:
        lines = snakefile_handle.readlines()

    assert (
        lines[6] == "models = ['DeepSEA/variantEffects', 'DeepSEA/beluga']\n"
    )

    with open(output_dir / "Snakefile.1", "r") as snakefile_handle:
        lines = snakefile_handle.readlines()

    assert lines[6] == "models = ['DeepSEA/predict', 'Basset']\n"


def test_cli_input_vcf_does_not_exist(runner):
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        ["in.vcf", "in.fa", "out_dir", "-mg", "DeepSEA", "-n", "2"],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_VCF'" in result.output


def test_cli_input_fasta_does_not_exist(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            "in.fa",
            "out_dir",
            "-mg",
            "DeepSEA",
            "-n",
            "2",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for 'INPUT_FASTA'" in result.output


def test_cli_output_dir_does_not_exist(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "-mg",
            "DeepSEA",
            "-mg",
            "Basset",
            "-n",
            "2",
        ],
    )
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_cli_wrong_model(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    output_dir.mkdir()
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "-mg",
            "Deepsea",
            "-n",
            "2",
        ],
    )
    assert result.exit_code == 2
    assert "Not adding Deepsea as it is not supported yet" in result.output


def test_cli_invalid_n(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    output_dir.mkdir()
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "-mg",
            "DeepSEA",
            "-mg",
            "Basset",
            "-n",
            "0",
        ],
    )
    assert result.exit_code == 2
    assert "Please enter a positive number of shards" in result.output


def test_cli_shard_greater_than_models(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent
    output_dir = tmp_path / "workflow"
    output_dir.mkdir()
    result = runner.invoke(
        snakefilegenerator.generate_snakefiles,
        [
            str(test_dir / "data" / "general" / "test.vcf"),
            str(test_dir / "data" / "general" / "hg38_chr22.fa"),
            str(output_dir),
            "-mg",
            "DeepSEA",
            "-mg",
            "Basset",
            "-n",
            "5",
        ],
    )
    assert result.exit_code == 2
    assert "Number of shards must be <= the number of models" in result.output
