from pathlib import Path
import numpy as np

from arcmapper.strategies import map, get_categorical_mapping

dictionary_file = Path(__file__).parent / "data" / "ccpuk_dictionary.csv"
arc_file = Path(__file__).parent / "data" / "ARCH.csv"

def test_get_categorical_mapping():
    sim = np.array([[0.1, 0.8], [0.9, 0.1]])
    target = ["male", "female"]
    source = ["femme", "homme"]
    assert get_categorical_mapping(source, target, sim) == {"femme": "female", "homme": "male"}
    

def test_tf_idf(data_dictionary, arc_schema):
    map("tf-idf", data_dictionary, arc_schema, num_matches=3)
    

