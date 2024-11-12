import ast
from collections import namedtuple

import pandas as pd
import numpy as np
import numpy.typing
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

SBERT_MODEL = "all-MiniLM-L6-v2"

Response = namedtuple("Response", ["val", "text"])
Response.__str__ = lambda self: f"{self.val}, {self.text}"


def get_match_dataframe_from_similarity_matrix(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    similarity_matrix: numpy.typing.ArrayLike,
    num_matches: int,
    threshold: float,
) -> pd.DataFrame:
    """Get mapping matches dataframe from a similarity matrix

    Parameters
    ----------
    dictionary
        Source data dictionary to map
    arc
        ARC data dictionary, can be read using :meth:`arcmapper.read_arc_schema`
    similarity_matrix
        Similarity matrix calculated using a strategy
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
    S = np.argsort(similarity_matrix, axis=1)[:, ::-1][:, :num_matches]

    match_df = pd.DataFrame(
        columns=[
            "status",
            "raw_variable",
            "raw_description",
            "raw_response",
            "arc_variable",
            "arc_description",
            "arc_response",
            "rank",
        ],
        data=sum(
            [
                [
                    [
                        "-",
                        dictionary.iloc[i].variable,
                        dictionary.iloc[i].description,
                        dictionary.iloc[i].responses,
                        arc.iloc[k].variable,
                        arc.iloc[k].description,
                        arc.iloc[k].responses,
                        j,
                    ]
                    for j, k in enumerate(S[i])
                    if similarity_matrix[i, S[i, j]] > threshold  # type: ignore
                ]
                for i in range(len(dictionary))
            ],
            [],
        ),
    )
    dictionary_categorical_vars = dictionary[pd.notnull(dictionary.responses)].variable
    arc_categorical_vars = arc[pd.notnull(arc.responses)].variable

    # drop (raw_variable, arc_variable) match pairs where only one of them
    # is of categorical type (answer options or responses present)
    if pd.notnull(dictionary.responses).any():
        return match_df[
            ~(
                match_df.raw_variable.isin(dictionary_categorical_vars)
                ^ match_df.arc_variable.isin(arc_categorical_vars)
            )
        ]
    else:
        # empty responses column in dictionary, indicating it was not supplied
        return match_df


def match_responses(
    source: list[Response], target: list[Response], sbert_model: str = SBERT_MODEL
) -> list[tuple[Response, Response]]:
    """Returns mapping of categorical values from source list to target list.
    Finds the closest match in target for each string in the source list. This
    is used to map categorical values from the source dictionary to ARC

    Example: in the source data dictionary, there is a `sex` variable which
    takes the values `man` and `woman`. ARC has a `demog_sex` variable which
    takes the values `male`, `female` and `unknown`. Then this function
    constructs a similarity matrix between [man, woman] and [male, female]
    would return

    .. code::

        [(("2", "man"),("1", "male")), (("1", "woman"), ("2", "female"))]

    Parameters
    ----------
    source
        Source mapping of response description to response, e.g.
        ``[("male", "1"), ("female": "2")]``
    target
        Target list of strings, usually from the ARC `responses` key
        e.g. ``[("men", "2"), ("woman", "1")]``
    sbert_model
        SBERT model to use (optional)

    Returns
    -------
    list[tuple[tuple[str, str], tuple[str, str]]]
        List of pairs of mappings of dictionary to ARC
    """
    model = SentenceTransformer(sbert_model)
    source_embeddings = model.encode([i.text for i in source])
    target_embeddings = model.encode([i.text for i in target])
    source_map: dict[str, str] = {v: k for k, v in source}
    target_map: dict[str, str] = {v: k for k, v in target}
    S = model.similarity(source_embeddings, target_embeddings).numpy()
    max_idx = np.argmax(S, axis=1)
    return [
        (
            Response(source_map[source[i].text], source[i].text),
            Response(target_map[target[max_idx[i]].text], target[max_idx[i]].text),
        )
        for i in range(len(source))
    ]


def has_valid_response(row) -> bool:
    return isinstance(row.raw_response, str) and isinstance(row.arc_response, str)


def infer_response_mapping(
    m: pd.DataFrame, sbert_model: str = SBERT_MODEL
) -> pd.DataFrame:
    """Infer response mapping from data dicitonary to ARC.

    This is a simplified version of the mapping that takes place in strategies
    """
    # data schema for m:
    #   raw_variable, raw_description, raw_response,
    #   arc_variable, arc_description, arc_response,
    out = []
    sbert_model = SentenceTransformer(sbert_model)

    for row in m.itertuples():
        if has_valid_response(row):
            raw_response = (
                row.raw_response
                if isinstance(row.raw_response, list)
                else ast.literal_eval(row.raw_response)
            )
            arc_response = (
                row.arc_response
                if isinstance(row.arc_response, list)
                else ast.literal_eval(row.arc_response)
            )
            s = list(map(lambda r: Response(*r), raw_response))
            t = list(map(lambda r: Response(*r), arc_response))
            out.extend(
                [
                    (
                        row.raw_variable,
                        row.raw_description,
                        str(sr),
                        row.arc_variable,
                        row.arc_description,
                        str(tr),
                    )
                    for sr, tr in match_responses(s, t)
                ]
            )
        else:
            out.append(
                (
                    row.raw_variable,
                    row.raw_description,
                    None,
                    row.arc_variable,
                    row.arc_description,
                    None,
                )
            )
    df = pd.DataFrame(
        out,
        columns=[
            "raw_variable",
            "raw_description",
            "raw_response",
            "arc_variable",
            "arc_description",
            "arc_response",
        ],
    )
    return df


def tf_idf(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    num_matches: int = 5,
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
    return get_match_dataframe_from_similarity_matrix(
        dictionary, arc, X.dot(Y.T).toarray(), num_matches, threshold
    )


def sbert(
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    model: str = "all-MiniLM-L6-v2",
    num_matches: int = 5,
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

    return get_match_dataframe_from_similarity_matrix(
        dictionary,
        arc,
        sbert_model.similarity(embeddings, arc_embeddings).numpy(),
        num_matches,
        threshold,
    )


def use_map(
    method: str,
    dictionary: pd.DataFrame,
    arc: pd.DataFrame,
    num_matches: int = 5,
) -> pd.DataFrame:
    match method:
        case "tf-idf":
            return tf_idf(dictionary, arc, num_matches)
        case "sbert":
            return sbert(dictionary, arc, num_matches=num_matches)
        case _:
            raise ValueError(f"Unknown mapping method: {method}")
