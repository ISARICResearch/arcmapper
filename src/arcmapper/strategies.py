import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .types import PossibleMatch

NUM_MATCHES = 3


def tf_idf(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    var_col: str = "variable",
    desc_col: str = "description",
) -> list[PossibleMatch]:
    assert "text" not in dictionary.columns
    dictionary_text = dictionary[var_col].str.replace("_", " ") + dictionary[desc_col]
    arc_text = arc["Variable"] + " " + arc["Question"]
    vec = TfidfVectorizer(max_df=0.9, ngram_range=(1, 2))
    X = vec.fit_transform(dictionary_text)
    Y = vec.transform(arc_text)

    # Similarity (this is the tf-idf bit.)
    D = Y.dot(X.T)

    sorted_indices = np.argsort(D.toarray(), axis=1)[:, ::-1]
    sorted_values = np.take_along_axis(D.toarray(), sorted_indices, axis=1)
    mask = sorted_values != 0
    filtered_indices = np.where(mask, sorted_indices, np.nan)
    # nans are given if no other similarities are found
    S = filtered_indices[:, :NUM_MATCHES]
