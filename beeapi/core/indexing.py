import functools
import os
import typing

from whoosh.filedb.filestore import FileStorage, RamStorage

from beeapi import constants as beeconst
from beeapi.core import apptypes
from beeapi.core.schemas import OFFDictSchema


def _get_indexer_by_type(idx_type):
    lookup = {
        beeconst.INDEXER_FILE: build_file_indexer,
        beeconst.INDEXER_RAM: build_ram_indexer,
    }
    builder = lookup[idx_type]
    return builder


def build_file_storage(index_dir=None, *args, **kwargs):
    _index_dir = index_dir or beeconst.DEFAULT_INDEX_DIR
    os.makedirs(_index_dir, exist_ok=True)

    storage = FileStorage(
        path=_index_dir
    )
    return storage


def build_ram_storage(*args, **kwargs):
    storage = RamStorage()
    return storage


def get_existing_index(storage, index_name=None) -> typing.Optional[apptypes.Index]:
    _index_name = index_name or beeconst.DEFAULT_INDEX_NAME

    index_exists = storage.index_exists(
        indexname=_index_name
    )

    maybe_index = (
        storage.open_index(
            indexname=_index_name,
            schema=OFFDictSchema,
        )
        if index_exists else None
    )

    return maybe_index


def build_index_from_storage(storage, index_name=None) -> apptypes.Index:
    _index_name = index_name or beeconst.DEFAULT_INDEX_NAME

    index = (
        get_existing_index(
            storage=storage,
            index_name=_index_name
        ) or storage.create_index(
            indexname=_index_name,
            schema=OFFDictSchema,
        )
    )
    return index


def index_exists(index_name=None, storage=None):
    _index_name = index_name or beeconst.DEFAULT_INDEX_NAME
    _storage = storage or build_file_storage()
    index = get_existing_index(
        storage=_storage,
        index_name=_index_name
    )
    return index


@functools.lru_cache(maxsize=5)
def build_file_indexer(index_dir=None, index_name=None):
    storage = build_file_storage(index_dir=index_dir)
    index = build_index_from_storage(
        storage=storage,
        index_name=index_name
    )
    return index


@functools.lru_cache(maxsize=5)
def build_ram_indexer(index_name=None):
    storage = build_ram_storage()
    index = build_index_from_storage(
        storage=storage,
        index_name=index_name
    )
    return index


def get_indexer(idx_type, *args, **kwargs):
    norm_idx_type = idx_type.lower()
    builder = _get_indexer_by_type(idx_type=norm_idx_type)
    indexer = builder(*args, **kwargs)
    return indexer


def add_document_to_index(original, stemmed, lineno, index=None, writer=None, commit=True, **kwargs):
    _writer = writer or index.writer(**kwargs)

    _writer.update_document(
        lineno=lineno,
        original=original,
        contents=original,
        stemmed=stemmed,
    )

    if commit:
        _writer.commit()

    return _writer
