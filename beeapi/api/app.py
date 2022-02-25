import typing

from fastapi import FastAPI

from beeapi.constants import DEFAULT_DICT_PATH
from beeapi.core.parsing import OFFCategoriesDictParser
from beeapi.core import apptypes
from beeapi.api import types as api_types


app = None


def get_config() -> api_types.ApiConfig:
    options = dict(
        debug=False,
        title="BeeAPI"
    )
    return options


def build_app(config: api_types.MaybeApiConfig = None) -> api_types.ApiApp:
    _config = config or get_config()
    new_app = FastAPI(**_config)
    return new_app


def build_index(config: api_types.MaybeApiConfig = None) -> apptypes.Index:
    _config = config or get_config()

    _index = OFFCategoriesDictParser.parse_cached(
        filepath=DEFAULT_DICT_PATH
    )
    return _index


def get_index_dependency(config: api_types.MaybeApiConfig = None) -> typing.Generator:
    _index = build_index(config=config)
    try:
        yield _index
    finally:
        pass


def get_app(
    config: api_types.MaybeApiConfig = None
) -> api_types.ApiApp:

    global app
    if config or not app:
        app = build_app(config=config)

    # even if we don't return it, we'll need it soon enough
    build_index(
        config=config
    )
    return app


def get_setup_bundle(
    config: api_types.MaybeApiConfig = None,
    app: typing.Optional[api_types.ApiApp] = None,
    with_index: typing.Optional[apptypes.Index] = None,
) -> api_types.SetupBundle:

    app = app or get_app(
        config=config
    )

    index = with_index or build_index(
        config=config
    )

    return app, index
