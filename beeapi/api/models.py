import typing

from pydantic import BaseModel
from beeapi.core import apptypes


class BasicResponseModel(BaseModel):
    results: typing.Union[str, dict]


class SimpleFallibleResponseModel(BasicResponseModel):
    error: str


class IndexResponseModel(BaseModel):
    endpoints: typing.Dict[str, str]


class JobResponseModel(BaseModel):
    results: list[apptypes.Phrase]


class AnnotatedJobResponseModel(JobResponseModel):
    README: typing.Optional[str]
