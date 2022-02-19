import pytest

from beeapi.core import trie


def test_trie_inits_default():
    test_trie = trie.Trie(maxdepth=None)
    assert test_trie.maxdepth == trie.Trie.DEFAULT_MAX_DEPTH


@pytest.mark.parametrize(
    ("maxdepth",), (
        (0,),
        (1,),
        (2,),
        (25,),
))
def test_trie_inits_custom_valid(maxdepth):
    test_trie = trie.Trie(maxdepth=maxdepth)
    assert test_trie.maxdepth == maxdepth


@pytest.mark.parametrize(
    ("maxdepth", "exception"), (
        (-1, ValueError),
        (-2, ValueError),
        (NotImplemented, TypeError),
))
def test_trie_inits_custom_invalid(maxdepth, exception):
    with pytest.raises(exception):
        trie.Trie(maxdepth=maxdepth)


def test_trie_insert_inplace():
    test_word = "test word"
    test_trie = trie.Trie(inplace_mode=False)

    assert len(test_trie) == 0

    test_trie.insert(test_word, in_place=True)
    assert len(test_trie) == 1

    assert test_word in test_trie


def test_trie_insert_immutable():
    test_word = "test word"
    test_trie = trie.Trie(inplace_mode=True)

    assert len(test_trie) == 0

    new_trie = test_trie.insert(test_word, in_place=False)
    assert len(test_trie) == 0
    assert len(new_trie) == 1

    assert test_word not in test_trie
    assert test_word in new_trie


@pytest.mark.parametrize(
    ("word", "lang", "expected"), (
        ("", None, ""),
        ("BooM", None, "boom"),
        ("BooM", "english", "boom"),
        ("LoRem iPsUM", None, "lorem ipsum"),
        ("LoRem iPsUM", "latin", "lorem ipsum"),
        ("UPPERCASE", None, "uppercase"),
        ("UPPERCASE", "english", "uppercase"),
))
def test_normalize_word(word, lang, expected):
    output = trie.Trie.normalize_item(word, language=lang)
    assert output == expected


@pytest.mark.parametrize(
    ("test_data", "prefix"), (
        ([], "a"),
        (("abcd", "ARGH", "Armageddon", "Able", "BooM"), "a"),
        (("abcd", "ARGH", "Armageddon", "Able", "BooM"), "b"),
        (("BooM", "book", "blame", "Actor", "ale"), "b"),
        (("BooM", "book", "blame", "Actor", "ale"), "bo"),
        (("BooM", "book", "blame", "Actor", "ale"), "BO"),
))
def test_get_prefix_matches(test_data, prefix):
    test_trie = trie.Trie.from_iterable(
        test_data,
        maxdepth=2
    )

    normalized_test_data = tuple((test_trie.normalize_item(data_itm) for data_itm in test_data))
    normalized_prefix = test_trie.normalize_item(prefix)

    matches = test_trie.get_prefix_matches(prefix)

    for word in normalized_test_data:
        if word.startswith(normalized_prefix):
            assert word in matches
        else:
            assert word not in matches


@pytest.mark.parametrize(
    ("inp_strings",), (
        ([],),
        (["abc", "def"],),
        (["DeG", "CaBBagE"],),
        (["abc", "def", "DeG", "CaBBagE"],),
        (["supercalifragilistic", "onomatopoeia"],),
        (["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."],),
))
def test_trie_from_iterable(inp_strings):
    test_trie = trie.Trie.from_iterable(inp_strings)
    assert len(test_trie) == len(inp_strings)
    for inp in inp_strings:
        assert inp in test_trie

