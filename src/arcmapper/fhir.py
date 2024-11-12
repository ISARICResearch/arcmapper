"""Final mapping of data dictionary to FHIR

Mapping file MUST conform to specification at
https://fhirflat.readthedocs.io/en/latest/spec/mapping.html
"""

import warnings
from pathlib import Path

import pandas as pd

from .strategies import infer_response_mapping

VALID_FHIR_RESOURCES = [
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


class FHIRMapping:
    "Loads mapping file from a Excel (XLSX) sheet"

    def __init__(self, file: str | Path):
        path = Path(file)
        if path.suffix != ".xlsx":
            raise ValueError("FHIRMapping only supports Excel sheets at the moment")
        index = pd.read_excel(path)
        if "Resources" not in index.columns:
            raise ValueError(
                "Required 'Resources' column not present in FHIR mapping file"
            )
        self.resources = sorted(set(index.Resources) & set(VALID_FHIR_RESOURCES))
        if "Patient" not in self.resources:
            raise ValueError(
                "Required FHIR mapping for FHIR resource 'Patient' not found in mapping file"
            )
        self.path = path

    def get_resource(self, resource: str) -> pd.DataFrame:
        "Gets resource from FHIR mapping Excel sheet"
        resource = resource.capitalize()  # capitalize first letter
        if resource not in self.resources:
            raise ValueError(
                f"Resource '{resource}' not found, valid resources: {self.resources}"
            )
        df = pd.read_excel(self.path, sheet_name=resource)

        # forward fill NaNs to enable merge with mapping frame
        df["raw_variable"] = df["raw_variable"].ffill()
        return df.rename(
            columns={"raw_variable": "arc_variable", "raw_response": "arc_response"}
        )


def merge(
    draft: pd.DataFrame, mapping: FHIRMapping, resources: list[str] = []
) -> dict[str, pd.DataFrame]:
    out = {}
    draft = infer_response_mapping(draft)
    for resource in resources or mapping.resources:
        # first generate choice responses for each mapping
        if resource not in mapping.resources:
            warnings.warn(
                f"Resource requested to be mapped but not found in mapping file: {resource}"
            )
        out[resource] = draft.merge(
            mapping.get_resource(resource), on=["arc_variable", "arc_response"]
        )
    return out


def format_merge(merged_data, selected_columns: list[str] | None = None):
    out = ""
    selected_columns = selected_columns or [
        "raw_variable",
        "raw_response",
        "arc_variable",
        "arc_response",
        "raw_description",
        "arc_description",
    ]
    for resource in merged_data:
        out += "{{{ resource " + resource + "\n"
        out += merged_data[resource][selected_columns].to_csv(index=False, sep="\t")
        out += "}}}\n"
    return out.strip()
