import csv
from pathlib import Path

from kipoi_veff2 import interval_based

import pytest


def test_interval_based_modelconfig():
    test_model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[
        "MMSplice/pathogenicity"
    ]
    assert test_model_config.model == "MMSplice/pathogenicity"
    assert (
        test_model_config.model_description.info.authors[0].name == "Jun Cheng"
    )
    assert (
        type(test_model_config.kipoi_model_with_dataloader).__name__
        == "MMSpliceModel"
    )


# TODO: Second item of pathogenecity output tuple is empty. Why?
@pytest.mark.parametrize(
    "model_name, header_name, variant_exon_id, number_of_headers,\
        number_of_rows",
    [
        (
            "MMSplice/modularPredictions",
            "MMSplice/modularPredictions/donor_ref_intron",
            "17:41197805:ACATCTGCC>A:ENSE00001814242",
            15,
            2035,
        ),
        (
            "MMSplice/deltaLogitPSI",
            "MMSplice/deltaLogitPSI/1",
            "17:41197805:ACATCTGCC>A:ENSE00001814242",
            6,
            2035,
        ),
        (
            "MMSplice/splicingEfficiency",
            "MMSplice/splicingEfficiency/1",
            "17:41197805:ACATCTGCC>A:ENSE00001814242",
            6,
            2035,
        ),
        (
            "MMSplice/mtsplice",
            "MMSplice/mtsplice/Whole_Blood",
            "17:41197805:ACATCTGCC>A:ENSE00001814242",
            61,
            2035,
        ),
    ],
)
def test_interval_based_scoring(
    model_name,
    header_name,
    variant_exon_id,
    number_of_headers,
    number_of_rows,
    tmp_path,
):
    interval_based_test_dir = (
        Path(__file__).resolve().parent / "data" / "interval-based"
    )
    vcf_file = str(interval_based_test_dir / "test.vcf")
    fasta_file = str(interval_based_test_dir / "test.fa")
    gtf_file = str(interval_based_test_dir / "test.gtf")
    output_file = tmp_path / f"out.{model_name.replace('/', '_')}.tsv"

    model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[model_name]
    interval_based.score_variants(
        model_config=model_config,
        vcf_file=vcf_file,
        fasta_file=fasta_file,
        gtf_file=gtf_file,
        output_file=output_file,
    )
    assert output_file.exists()
    with open(output_file, "r") as output_file_handle:
        tsv_reader = csv.reader(output_file_handle, delimiter="\t")
        assert len(list(tsv_reader)) == number_of_rows
    with open(output_file, "r") as output_file_handle:
        tsv_reader = csv.reader(output_file_handle, delimiter="\t")
        header = next(tsv_reader)
        assert len(header) == number_of_headers
        assert header[number_of_headers - 1] == header_name
        row = next(tsv_reader)
        assert row[2] == variant_exon_id
        assert len(row) == number_of_headers
