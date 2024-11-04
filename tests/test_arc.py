"Module to read ARC schema"

from pathlib import Path

from arcmapper.arc import arc_schema_url, read_arc_schema


def test_arc_schema_url():
    assert (
        arc_schema_url("1.0.0")
        == "https://github.com/ISARICResearch/DataPlatform/raw/refs/heads/main/ARCH/ARCH1.0.0/ARCH.csv"
    )


def test_read_arc_schema():
    arc = read_arc_schema(str(Path(__file__).parent / "data" / "ARCH.csv"))
    print(arc)
