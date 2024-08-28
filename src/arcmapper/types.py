from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class MatchItem:
    variable: str
    description: str
    responses: str


class PossibleMatch(NamedTuple):
    raw_variable: str
    raw_response: str
    arc_variable: str
    arc_response: str
    weight: float
