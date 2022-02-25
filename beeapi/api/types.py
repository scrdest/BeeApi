import typing

import fastapi

from beeapi.core import apptypes

ApiConfig = dict
MaybeApiConfig = typing.Optional[ApiConfig]

ResponsePhrases = typing.Container[apptypes.Phrase]

ApiApp = fastapi.FastAPI
ApiIndex = apptypes.Index
SetupBundle = tuple[ApiApp, ApiIndex]
