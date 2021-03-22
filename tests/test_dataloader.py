from click.testing import CliRunner
from pathlib import Path

import pytest

from kipoi_veff2 import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_dataloader(runner):
    test_dir = Path(__file__).resolve().parent
    result = runner.invoke(
        cli.score_variants,
        [
            str(test_dir / "data" / "test.vcf"),
            str(test_dir / "data" / "hg38_chr22.fa"),
            str(test_dir / "data" / "out.vcf"),
            "-m",
            "DeepSEA/predict",
        ],
    )
    assert result.exit_code == 0
