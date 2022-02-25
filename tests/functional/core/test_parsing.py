from beeapi.constants import DEFAULT_DICT_PATH
from beeapi.core import apptypes
from beeapi.core.parsing import OFFCategoriesDictParser
from beeapi.core.queryhandler import run_query


def test_sample_dict():
    index: apptypes.Index = OFFCategoriesDictParser.parse_cached(filepath=DEFAULT_DICT_PATH)

    raw_testwords = [
        ("cauliflower cheese", "cauliflower cheese"),
        ("Red VeLVet caKe", "red velvet cake"),
        ("Red VeLVet caKeS", "red velvet cake"),
        ("apple juices", "apple juices"),
        ("apple juice", "apple juices"),
        ("Apple. Juice", "apple juices"),
    ]

    for test_word, expected_match in raw_testwords:
        top_matches = run_query(
            user_query=test_word,
            index=index,
        )
        assert top_matches
        best_match = top_matches[0]
        assert best_match == expected_match


