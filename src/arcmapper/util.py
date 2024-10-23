"Utility functions for arcmapper"

import io
import warnings
import urllib.request
from pathlib import Path

import chardet
import pandas as pd

from .types import Responses


def read_data(file_or_dataframe: str | pd.DataFrame) -> pd.DataFrame:
    if isinstance(file_or_dataframe, pd.DataFrame):
        return file_or_dataframe
    file = Path(file_or_dataframe)
    match file.suffix:
        case ".xlsx":
            return pd.read_excel(file)
        case ".csv":
            return pd.read_csv(file)


def read_csv_with_encoding_detection(file_or_url: str) -> pd.DataFrame:
    "Reads CSV file with encoding detection"

    if not file_or_url.endswith(".csv"):
        warnings.warn("File or URL supplied does not end with .csv extension")
    if file_or_url.startswith("http://") or file_or_url.startswith("https://"):
        data = urllib.request.urlopen(file_or_url).read()
    else:
        with open(file_or_url, "rb") as fp:
            data = fp.read()
    encoding = chardet.detect(data)["encoding"]
    decoded_data = data.decode(encoding)
    return pd.read_csv(io.StringIO(decoded_data))


def parse_redcap_response(s: str) -> Responses:
    return [tuple([x.strip() for x in r.split(",")]) for r in s.split("|")]
