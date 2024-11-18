"Types used in arcmapper"

from typing import NamedTuple, Literal

# Responses is either a list of valid responses for this variable
# example: gender = ["male", "female"]
# or it is a list of string -> string mappings, where the left side
# string is the value stored in the database, but the right hand side
# is the value as interpreted by arcmapper.
# example: gender = [(1, "male"), (2, "female")]
Responses = list[str] | list[tuple[str | int, str]]

DataType = Literal["enum", "number", "string", "date", "multiselect"]


class PossibleMatch(NamedTuple):
    raw_variable: str
    raw_response: str
    arc_variable: str
    arc_response: str
    weight: float
