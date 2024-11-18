"Utility functions for arcmapper"

import pytest
from pathlib import Path

import pandas as pd

from arcmapper.util import (
    read_data,
    read_csv_with_encoding_detection,
    parse_redcap_response,
    read_upload_data,
)

EXCEL_BASE64 = "something," + Path(__file__).with_name("excel_encoded.txt").read_text()
CSV_BASE64 = "something,dmFyaWFibGUsZGVzY3JpcHRpb24Kc3ViamlkLFN1YmplY3QgSUQKZ2VuLEdlbmRlciBvZiB0aGUgcGF0aWVudAo="


def test_read_data():
    arc_path = str(Path(__file__).parent / "data" / "ARCH.csv")
    assert isinstance(read_data(arc_path), pd.DataFrame)


def test_read_csv_with_encoding_detection():
    "Reads CSV file with encoding detection"

    arc_path = str(Path(__file__).parent / "data" / "ARCH.csv")
    assert isinstance(read_csv_with_encoding_detection(arc_path), pd.DataFrame)


@pytest.mark.parametrize(
    "contents,filename,expected",
    [
        (EXCEL_BASE64, "file.xlsx", {"subjid": [1, 2], "gender": ["female", "male"]}),
        (
            CSV_BASE64,
            "file.csv",
            {
                "variable": ["subjid", "gen"],
                "description": ["Subject ID", "Gender of the patient"],
            },
        ),
    ],
)
def test_read_upload_data(contents, filename, expected):
    df = read_upload_data(contents, filename)
    assert df is not None
    print(pd.DataFrame(expected))
    print(df)
    assert df.equals(pd.DataFrame(expected))


def test_read_upload_data_valid_extension():
    assert read_upload_data(CSV_BASE64, "test.txt") is None


def test_parse_redcap_response():
    assert parse_redcap_response("1, male | 2, female") == [
        ("1", "male"),
        ("2", "female"),
    ]
