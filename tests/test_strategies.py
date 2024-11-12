from arcmapper.strategies import use_map, match_responses, Response


def test_match_responses():
    source = [Response("1", "women"), Response("2", "men")]
    target = [Response("1", "male"), Response("2", "female")]
    assert match_responses(source, target) == [
        (("1", "women"), ("2", "female")),
        (("2", "men"), ("1", "male")),
    ]


def test_tf_idf(data_dictionary, arc_schema):
    use_map("tf-idf", data_dictionary, arc_schema, num_matches=3)
