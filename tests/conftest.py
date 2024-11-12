"Common fixtures"

from pathlib import Path

import pytest

import arcmapper

dictionary_file = str(
    Path(__file__).parent
    / "data"
    / "CCPUKSARIEastMidlands_DataDictionary_2022-06-06.csv"
)
arc_file = str(Path(__file__).parent / "data" / "ARCH.csv")


@pytest.fixture(scope="session")
def arc_schema():
    return arcmapper.read_arc_schema(arc_file)


@pytest.fixture(scope="session")
def data_dictionary():
    return arcmapper.read_data_dictionary(
        dictionary_file,
        description_field="Field Label",
        response_field="Choices, Calculations, OR Slider Labels",
        response_func="redcap",
    )
