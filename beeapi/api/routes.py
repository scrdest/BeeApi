from fastapi import Depends

from beeapi import constants as beeconsts
from beeapi.core.indexing import add_document_to_index, get_existing_index, build_file_storage, index_exists
from beeapi.core.queryhandler import run_query

from beeapi.api import models, types as api_types, apiconstants
from beeapi.api.app import get_app, get_index_dependency

app = get_app()


@app.get("/", response_model=models.IndexResponseModel)
async def root():
    jobs_readme = (
        "Send a POST request to this endpoint to submit jobs (requires the ?text='yourtext' parameter).",
        "For demo purposes, this endpoint also accepts GET requests with the same parameter sets.",
    )

    return {
        "endpoints": {
            "/": "This page.",
            apiconstants.JOBS_ENDPOINT: " ".join(jobs_readme),
            apiconstants.DICT_ENDPOINT: "Represents the indexed dictionary. GET to check if index exists.",
        }
    }


async def _generic_new_job(text: str, index: api_types.ApiIndex) -> api_types.ResponsePhrases:
    matches = run_query(
        user_query=text,
        index=index,
    )

    msg = matches
    return msg


@app.post(apiconstants.JOBS_ENDPOINT, response_model=models.JobResponseModel)
async def new_job(text: str, index: api_types.ApiIndex = Depends(get_index_dependency)):
    # NOTE: this is a pretty slow job (10s+ latency under 100-user load); this would
    # almost certainly benefit from BackgroundTasks or a message queue and job system,
    # but I don't want to set up a whole pile of architecture just to support doing
    # that in the demo version.
    result = await _generic_new_job(
        text=text,
        index=index
    )
    response = {
        "results": result
    }
    return response


@app.get(
    apiconstants.JOBS_ENDPOINT,
    response_model=models.AnnotatedJobResponseModel,
    response_model_exclude_unset=True,
)
async def new_job_demo(text: str, index: api_types.ApiIndex = Depends(get_index_dependency)):
    result = await _generic_new_job(
        text=text,
        index=index
    )

    msg = {
        "README": "While this is not proper REST API design, this endpoint had been left in to make it easy to demo the API.",
        "results": result
    }
    return msg


@app.put(f"/{apiconstants.DICT_ENDPOINT}/<lineno>")
async def add_document(
    lineno: int,
    original: str,
    stemmed: str,
    index: api_types.ApiIndex = Depends(get_index_dependency)
):
    try:
        add_document_to_index(
            original=original,
            stemmed=stemmed,
            lineno=lineno,
            index=index,
            commit=True
        )

    except Exception as E:
        msg = {
            "response": "failed to add document",
            "error": E
        }

    else:
        msg = {
            "response": "document added successfully"
        }

    return msg


@app.get(f"{apiconstants.DICT_ENDPOINT}", response_model=models.BasicResponseModel)
async def get_index(index_name: str = None):
    _index_name = index_name or beeconsts.DEFAULT_INDEX_NAME
    index = index_exists(index_name=_index_name)

    if index:
        msg = {
            "results": {
                "name": _index_name,
                "doc_count": index.doc_count(),
            }
        }

    else:
        msg = {
            "results": f"Index `{_index_name}` does not exist."
        }

    return msg


@app.delete(f"{apiconstants.DICT_ENDPOINT}", response_model=models.BasicResponseModel)
async def get_index(index_name: str = None):
    _index_name = index_name or beeconsts.DEFAULT_INDEX_NAME
    index = index_exists(index_name=_index_name)

    if index:
        import shutil
        try:
            shutil.rmtree(
                beeconsts.DEFAULT_INDEX_DIR
            )

        except Exception as E:
            msg = {
                "results": {
                    "success": False,
                    "message": E,
                }
            }

        else:
            msg = {
                "results": {
                    "success": True,
                    "message": f"Index `{_index_name}` has been deleted successfully.",
                }
            }

    else:
        msg = {
            "results": f"Index `{_index_name}` does not exist."
        }

    return msg


@app.put(f"/{apiconstants.DICT_ENDPOINT}")
async def add_document(
    lineno: int,
    original: str,
    stemmed: str,
    index: api_types.ApiIndex = Depends(get_index)
):
    try:
        add_document_to_index(
            original=original,
            stemmed=stemmed,
            lineno=lineno,
            index=index,
            commit=True
        )

    except Exception as E:
        msg = {
            "response": "failed to add document",
            "error": E
        }

    else:
        msg = {
            "response": "document added successfully"
        }

    return msg
