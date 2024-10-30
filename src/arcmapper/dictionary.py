"""Types and methods for loading data dictionaries"""

import json
import operator
from typing import Any, NamedTuple

import pandas as pd
from pandas.api.types import is_object_dtype
from .types import DataType
from .util import read_data, parse_redcap_response

RESPONSE_PARSERS = {"redcap": parse_redcap_response}


class DictionaryField(NamedTuple):
    "Data dictionary field"

    variable: str
    description: str
    responses: str | None
    type: DataType


def read_data_dictionary(
    source: str | pd.DataFrame,
    variable_field: str | None = None,
    description_field: str | None = None,
    type_field: str | None = None,
    response_field: str | None = None,
    response_func: str | None = None,
) -> pd.DataFrame:
    """Reads from data dictionary file or data frame

    By default, form responses (categorical enumerations) are not read, as
    there is no standard format. This can be changed by setting *both*
    response_field and response_func to return responses.

    Parameters
    ----------
    source
        Data dictionary to read. Can also pass a dataframe instead of a file
    variable_field
        Field to use for variable name. If not specified, uses the first
        column
    description_field
        Field to use for description. If not specified, is taken to be the
        stringly typed column with the maximum mean length.
    type_field
        Field to use for type information. If not specified, every type
        defaults to 'string'
    response_field
        Response field to use
    response_func
        Function that takes a string and returns a Responses type

    Returns
    -------
    pd.DataFrame
        Data dictionary
    """
    dd = read_data(source)
    variable_field = variable_field or dd.columns[0]
    if description_field is None:
        description_field = max(
            (
                (c, dd[c].map(lambda x: len(x) if isinstance(x, str) else 0).mean())
                for c in dd.columns
                if is_object_dtype(dd[c])
            ),
            key=operator.itemgetter(1),
        )[0]
    if (response_field is None) ^ (response_func is None):
        raise ValueError("Both response_field and response_func have to be specified")
    assert (
        response_func in RESPONSE_PARSERS
    ), f"Unknown response parser: {response_func}"
    return pd.DataFrame(
        [
            DictionaryField(
                row[variable_field],
                row[description_field],
                RESPONSE_PARSERS[response_func](row[response_field])
                if response_field and isinstance(row[response_field], str)
                else None,
                row[type_field] if type_field else "string",
            )
            for row in dd.to_dict(orient="records")
        ]
    )


def read_from_data(data: str | pd.DataFrame) -> pd.DataFrame:
    "Infers data dictionary from sample data"
    raise NotImplementedError


def read_from_jsonschema(data: str | dict[str, Any]) -> pd.DataFrame:  # type: ignore
    "Returns DataDictionary from JSON Schema file or data"
    if isinstance(data, str):
        data: dict[str, Any] = json.loads(data)
    dd = []
    variables = data["properties"]
    for v in variables:
        t = variables[v].get("type","string")
        if "enum" in variables[v]:
            dd.append((v, variables[v].get("description", ""), [(x, x) for x in variables[v]["enum"]], 'categorical'))
        else:
            dd.append((v, variables[v].get("description", ""), None, t))
    return pd.DataFrame(dd, columns=["variable", "description", "responses", "type"])
