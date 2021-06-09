from pathlib import Path

from click.testing import CliRunner
import pandas as pd
import pytest

from kipoi_veff2 import merge


@pytest.fixture
def runner():
    runner = CliRunner()
    yield runner


def test_cli_correct_use_merge(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent / "data" / "general"
    merged_file_path = tmp_path / "merged.tsv"
    result = runner.invoke(
        merge.merge,
        [
            str(test_dir / "out.Basset.tsv"),
            str(test_dir / "out.DeepSEA.predict.tsv"),
            str(merged_file_path),
        ],
    )
    assert result.exit_code == 0
    assert merged_file_path.exists()

    df_generated = pd.read_csv(str(merged_file_path), sep="\t")
    df_expected = pd.read_csv(
        str(test_dir / "merged.Basset.DeepSEA.predict.tsv"), sep="\t"
    )

    assert sorted(df_expected.columns) == sorted(df_generated.columns)
    assert len(df_expected.index) == len(df_generated.index)
    assert (
        df_expected.columns.values.tolist()
        == df_generated.columns.values.tolist()
    )  # TODO: Should I add sorted here?


def test_cli_no_input(runner):
    result = runner.invoke(
        merge.merge,
        [],
    )
    assert result.exit_code == 2
    assert "Missing argument 'INPUT_TSVS...'" in result.output


def test_cli_single_input_no_output(runner):
    result = runner.invoke(
        merge.merge,
        ["randominput.tsv"],
    )
    assert result.exit_code == 2
    assert "Missing argument 'INPUT_TSVS...'" in result.output


def test_cli_invalid_input(runner):
    result = runner.invoke(
        merge.merge,
        [
            "randominput.tsv",
            "randomoutput.tsv",
        ],
    )
    assert result.exit_code == 2
    assert "Path 'randominput.tsv' does not exist" in result.output


def test_cli_single_input(runner, tmp_path):
    test_dir = Path(__file__).resolve().parent / "data" / "general"
    input_file_path = test_dir / "out.Basset.tsv"
    output_file_path = tmp_path / "randomoutput.tsv"
    result = runner.invoke(
        merge.merge,
        [
            str(input_file_path),
            str(output_file_path),
        ],
    )
    assert result.exit_code == 0
    assert output_file_path.exists()
    df_generated = pd.read_csv(str(output_file_path), sep="\t")
    df_expected = pd.read_csv(str(input_file_path), sep="\t")
    assert sorted(df_expected.columns) == sorted(df_generated.columns)
    assert len(df_expected.index) == len(df_generated.index)
    assert (
        df_expected.columns.values.tolist()
        == df_generated.columns.values.tolist()
    )  # TODO: Should I add sorted here?
