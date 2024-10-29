"Module to read ARC schema"

import pandas as pd

from .types import DataType
from .util import read_csv_with_encoding_detection
from .dictionary import read_data_dictionary


def arc_schema_url(arc_version: str) -> str:
    return f"https://github.com/ISARICResearch/DataPlatform/raw/refs/heads/main/ARCH/ARCH{arc_version}/ARCH.csv"



def read_arc_schema(
    arc_version_or_file: str, preset: str | None = None
) -> pd.DataFrame:
    types_mapping: dict[str, DataType] = {
        "radio": "categorical",
        "number": "number",
        "text": "string",
        "date_dmy": "date",
        "checkbox": "categorical",
        "dropdown": "categorical",
        "datetime_dmy": "date",
    }
    arc_location = (
        arc_version_or_file
        if arc_version_or_file.endswith(".csv")
        else arc_schema_url(arc_version_or_file)
    )
    arc = read_csv_with_encoding_detection(arc_location)
    arc["Description"] = arc.Question + " " + arc.Definition
    arc["Type"] = arc.Type.map(types_mapping)
    dd = read_data_dictionary(
        arc,
        variable_field="Variable",
        description_field="Description",
        type_field="Type",
        response_field="Answer Options",
        response_func="redcap",
    )
    dd = dd[~pd.isna(dd.description)]
    if preset:
        preset_col = "preset_" + preset
        if preset_col not in arc.columns:
            raise ValueError(f"No such preset column exists in ARC: {preset_col}")
        dd = dd[dd[preset_col] == 1]
    return dd
