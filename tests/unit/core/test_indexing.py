import pytest
from beeapi.core import indexing


@pytest.mark.parametrize("idxtype, expected", (
    ("file", indexing.build_file_indexer),
    ("ram", indexing.build_ram_indexer),
))
def test_get_indexer_by_type(idxtype, expected):
    result = indexing._get_indexer_by_type(idxtype)
    assert result == expected


def test_build_ram_storage():
    result = indexing.build_ram_storage()
    assert result
    assert isinstance(result, indexing.RamStorage)

