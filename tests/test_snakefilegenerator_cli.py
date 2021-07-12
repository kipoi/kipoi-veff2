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
