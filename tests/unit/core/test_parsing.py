import pytest

from beeapi.core import parsing


@pytest.mark.parametrize("qry, expected", (
    ("apple", ["apple"]),
    ("apple juice", ["apple", "juice"]),
    ("apple, juice", ["apple", "juice"]),
    ("apple,juice", ["apple", "juice"]),
    ("apple,juice milk", ["apple", "juice", "milk"]),
    ("apple,juice.milk", ["apple", "juice", "milk"]),
    (",juice milk", ["juice", "milk"]),
    (",juice-milk", ["juice", "milk"]),
))
def test_parse_query(qry, expected):
    result = parsing.parse_query(qry)
    assert result
