from pathlib import Path

import pandas as pd

from arcmapper.fhir import FHIRMapping, merge, format_merge

MAPPING = Path(__file__).parent.parent / "arc-fhir" / "ARC_pre_1.0.0_preset_dengue.xlsx"
DRAFT_MAPPING = Path(__file__).parent / "data" / "arcmapper-mapping-file.csv"


def test_fhir_mapping():
    m = FHIRMapping(MAPPING)
    assert m.resources == [
        "Condition",
        "DiagnosticReport",
        "Encounter",
        "Immunization",
        "MedicationAdministration",
        "MedicationStatement",
        "Observation",
        "Patient",
        "Procedure",
        "Specimen",
    ]

    encounter = m.get_resource("encounter")
    assert {"arc_variable", "arc_response"} <= set(encounter.columns)


def test_merge(snapshot):
    draft_mapping = pd.read_csv(DRAFT_MAPPING)
    fhir_mapping = FHIRMapping(MAPPING)
    data = merge(draft_mapping, fhir_mapping, resources=["Patient"])
    assert format_merge(data) == snapshot
