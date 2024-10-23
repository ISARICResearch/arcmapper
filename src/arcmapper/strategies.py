import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer


def tf_idf(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    num_matches: int = 3,
    threshold: float = 0.3,
) -> pd.DataFrame:
    """Uses TF-IDF (text frequency - inverse document frequency) technique for mapping

    Parameters
    ----------
    dictionary
        Source data dictionary to map
    arc
        ARC data dictionary, can be read using :meth:`arcmapper.read_arc_schema`
    num_matches
        Number of matches to return
    threshold
        Similarity threshold beyond which a match is reported (upto num_matches).
        A lower similarity threshold will return more matches, which are potentially
        incorrect (higher false positive ratio), while a higher threshold will
        reduce the number of matches, but potentially miss out on correct matches
        as well (low false positive, higher false negative ratio)

    Returns
    -------
    pd.DataFrame
        Dataframe containing `raw_variable`, `arc_variable` and `rank` columns
        where `rank` is a number from 0 to num_matches - 1 indicating the fitness
        of the match, with 0 indicating highest similarity.
    """
    dictionary_text = dictionary.variable.str.replace(
        "_", " "
    ) + dictionary.description.map(lambda x: x if isinstance(x, str) else "")
    arc_text = arc.variable.str.replace("_", " ") + " " + arc.description
    vec = TfidfVectorizer(max_df=0.9, ngram_range=(1, 2))
    X = vec.fit_transform(dictionary_text)
    Y = vec.transform(arc_text)

    # Similarity (this is the tf-idf bit.)
    D = X.dot(Y.T).toarray()

    S = np.argsort(D, axis=1)[:, ::-1][:, :num_matches]

    match_df = pd.DataFrame(
        columns=["raw_variable", "arc_variable", "rank"],
        data=sum(
            [
                [
                    [
                        dictionary.iloc[i].variable,
                        arc.iloc[k].variable,
                        j,
                    ]
                    for j, k in enumerate(S[i])
                    if D[i, S[i, j]] > threshold
                ]
                for i in range(len(dictionary))
            ],
            [],
        ),
    )
    return match_df


def sbert(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    model: str = "all-MiniLM-L6-v2",
    num_matches: int = 3,
    threshold: float = 0.3,
) -> pd.DataFrame:
    """Uses sentence transformers (https://sbert.net) technique for mapping

    Using SBERT gives semantic similarity embeddings, which is useful for
    comparing words similar in meaning but syntactically different, such
    as 'death' and 'deceased', or 'NSAIDs' and 'ibuprofen'.

    Parameters
    ----------
    dictionary
        Source data dictionary to map
    arc
        ARC data dictionary, can be read using :meth:`arcmapper.read_arc_schema`
    model
        Embedding model to use
    num_matches
        Number of matches to return
    threshold
        Similarity threshold beyond which a match is reported (upto num_matches).
        A lower similarity threshold will return more matches, which are potentially
        incorrect (higher false positive ratio), while a higher threshold will
        reduce the number of matches, but potentially miss out on correct matches
        as well (low false positive, higher false negative ratio)

    Returns
    -------
    pd.DataFrame
        Dataframe containing `raw_variable`, `arc_variable` and `rank` columns
        where `rank` is a number from 0 to num_matches - 1 indicating the fitness
        of the match, with 0 indicating highest similarity.
    """
    dictionary_text = list(
        dictionary.variable.astype(str).replace("_", " ")
        + dictionary.description.map(lambda x: x if isinstance(x, str) else "")
    )
    arc_text = list(
        arc.variable.astype(str).replace("_", " ") + " " + arc.description.astype(str)
    )

    sbert_model = SentenceTransformer(model)

    embeddings = sbert_model.encode(dictionary_text)
    arc_embeddings = sbert_model.encode(arc_text)

    D = sbert_model.similarity(embeddings, arc_embeddings).numpy()
    S = np.argsort(D, axis=1)[:, ::-1][:, :num_matches]

    match_df = pd.DataFrame(
        columns=["raw_variable", "arc_variable", "rank"],
        data=sum(
            [
                [
                    [
                        dictionary.iloc[i].variable,
                        arc.iloc[k].variable,
                        j,
                    ]
                    for j, k in enumerate(S[i])
                    if D[i, S[i, j]] > threshold
                ]
                for i in range(len(dictionary))
            ],
            [],
        ),
    )
    return match_df
