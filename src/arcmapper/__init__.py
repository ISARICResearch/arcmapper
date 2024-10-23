import pandas as pd
from .arc import read_arc_schema
from .dictionary import read_data_dictionary
from .strategies import tf_idf, sbert


def map(
    method: str,
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    num_matches: int = 3,
    **kwargs,
) -> pd.DataFrame:
    match method:
        case "tf-idf":
            return tf_idf(dictionary, arc, num_matches)
        case "sbert":
            return sbert(dictionary, arc, num_matches=num_matches)
        case _:
            raise ValueError(f"Unknown mapping method: {method}")


__all__ = ["read_arc_schema", "map", "read_data_dictionary"]
