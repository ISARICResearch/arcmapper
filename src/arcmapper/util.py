"Utility functions for arcmapper"

from pathlib import Path
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


def parse_redcap_response(s: str) -> Responses:
    return [tuple([x.strip() for x in r.split(",")]) for r in s.split("|")]
