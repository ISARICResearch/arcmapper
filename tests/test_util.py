"Utility functions for arcmapper"
from pathlib import Path

import pandas as pd

from arcmapper.util import read_data, read_csv_with_encoding_detection, parse_redcap_response

def test_read_data():
    arc_path = str(Path(__file__).parent / 'data' / 'ARCH.csv')
    assert isinstance(read_data(arc_path), pd.DataFrame)

def test_read_csv_with_encoding_detection():
    "Reads CSV file with encoding detection"

    arc_path = str(Path(__file__).parent / 'data' / 'ARCH.csv')
    assert isinstance(read_csv_with_encoding_detection(arc_path), pd.DataFrame)

def test_parse_redcap_response():
    assert parse_redcap_response("1, male | 2, female") == [("1", "male"), ("2", "female")]
