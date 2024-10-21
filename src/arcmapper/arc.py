"Module to read ARC schema"

import pandas as pd

from .types import DataType
from .util import parse_redcap_response
from .dictionary import read_data_dictionary


def arc_schema_url(arc_version: str) -> str:
    return f"https://github.com/ISARICResearch/DataPlatform/raw/refs/heads/main/ARCH/ARCH{arc_version}/ARCH.csv"


def read_arc_schema(arc_version: str, preset: str | None = None) -> pd.DataFrame:
    types_mapping: dict[str, DataType] = {
        "radio": "categorical",
        "number": "number",
        "text": "string",
        "date_dmy": "date",
        "checkbox": "categorical",
        "dropdown": "categorical",
        "datetime_dmy": "date",
    }
    arc = pd.read_csv(arc_schema_url(arc_version))
    arc["Description"] = arc.Question + " " + arc.Definition
    arc["Type"] = arc.Type.map(types_mapping)
    dd = read_data_dictionary(
        arc, "Variable", "Description", "Type", "Answer Options", parse_redcap_response
    )
    if preset:
        preset_col = "preset_" + preset
        if preset_col not in arc.columns:
            raise ValueError(f"No such preset column exists in ARC: {preset_col}")
        dd = dd[dd[preset_col] == 1]
    return dd
