import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def tf_idf(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    num_matches: int = 3,
) -> pd.DataFrame:
    assert "text" not in dictionary.columns
    dictionary_text = dictionary.variable.str.replace(
        "_", " "
    ) + dictionary.description.map(lambda x: x if isinstance(x, str) else "")
    arc_text = arc.variable.str.replace("_", " ") + " " + arc.description
    vec = TfidfVectorizer(max_df=0.9, ngram_range=(1, 2))
    X = vec.fit_transform(dictionary_text)
    Y = vec.transform(arc_text)

    # Similarity (this is the tf-idf bit.)
    D = X.dot(Y.T)

    S = np.argsort(D.toarray(), axis=1)[:, ::-1][:, :num_matches]
    # nans are given if no other similarities are found
    match_df = pd.DataFrame(
        columns=["raw_variable", "arc_variable", "tf_rank"],
        data=sum(
            [
                [
                    [
                        dictionary.iloc[i].variable,
                        arc.iloc[k].variable,
                        j,
                    ]
                    for j, k in enumerate(S[i])
                ]
                for i in range(len(dictionary))
            ],
            [],
        ),
    )
    return match_df
