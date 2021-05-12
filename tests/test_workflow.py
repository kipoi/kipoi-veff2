from pathlib import Path

import pandas as pd


def test_snakemake_workflow():
    assert Path("tests/output.merged.tsv").exists()
    df_merged = pd.read_csv("tests/output.merged.tsv", sep="\t")
    assert len(df_merged) == 3075
    assert len(df_merged.columns) == 389
