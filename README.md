# BeeAPI

## Overview:

Given a natural-language string, this app returns a list of phrases in the stored
dictionary which match the phrases in the input.

The matches are exhaustive to the best effort; i.e. if a phrase matches both 'apple' and 
'apple juice', both _may_ be returned in the search.


## App Design:

This app had been designed to operate either as a REST API and a simple CLI app (or even
both in parallel, if you wish to run it this way).

The two modes of operation are designed to wrap a user I/O layer over a common app core.

The (excellent) [Invoke library](https://www.pyinvoke.org/) is used to provide a 
friendlier, Make-like interface to build and execution logic. 

The commands are wrapped in the `beemgmt` program. This program is callable either as-is, 
if you install the project as a package, or via `python -m beeapi.mgmt` from project files. 
Additionally, in the latter case, you can also use `inv/invoke` instead. 

Where possible, both pure terminal commands and their Invoke equivalents will be provided,
prefixed with 'COMMAND:' and 'INVOKE:' respectively.

[Poetry](https://python-poetry.org) had been used for build, dependency and virtualenv management. 

As such to use the commands, either enter the environment using `poetry shell` 
or prefix each command with `poetry run` if using the project files directly
(as opposed to installing this as a package - in which case, follow your env manager
of choice's equivalent conventions instead, e.g. `venv activate`).


### = CLI =

COMMAND: `python -m beeapi.cli`

INVOKE: `beemgmt run-app` (app)
INVOKE: `beemgmt run-query --query <text>` (one-off)

The CLI is currently extremely basic, with no real configuration options available.

The only caveat is the BEEAPI_MAIN_RUN_LOOPED envvar:
- BEEAPI_MAIN_RUN_LOOPED = true - run as app (equivalent to the first Invoke option)
- otherwise - run a one-off script (equivalent to the second Invoke option)


### = API =

COMMAND: `python -m beeapi.api [--port <port>] [--workers <workers>]`

INVOKE: `beemgmt run-api [--port <port>] [--workers <workers>]` 

The REST API has been built around [FastAPI](https://fastapi.tiangolo.com/)

The API is served on port 8080 by default; 
this can be changed by the `--port` option above.

The API is served on [Uvicorn](https://www.uvicorn.org) by default.

The primary endpoint is the `/jobs` endpoint. This endpoint accepts POST requests
with `text` as a parameter (i.e. `<host>/jobs?text=<some text>`). The parameter is
interpreted as the natural language query for the app.

For convenience of demonstration, the endpoint has been configured to work with GET
requests as well; keep in mind that these are not proper RESTful semantics and are
here purely for easy testing using standard browsers.


## - Core -

Most of the core heavy lifting is done using the Python [Whoosh library](https://whoosh.readthedocs.io).

Whoosh provides efficient indexing for the input dictionary, with the index
persisted to local file storage - which means we do not spend time rebuilding it
unnecessarily on server/app restarts.

Whoosh also provides the backend logic for the main querying logic.

The index search is then additionally processed using the 
**Unholy Pile of Heuristics(TM)** (**_UPoH_**) to refine the results.

This is, unfortunately, not an ideal and/or perfect algorithm. Unfortunately, classic NLP 
techniques like stemming are not viable as a (full) solution, as the search algorithm needs 
to support multiple target languages and NOT require a user to specify the query language.

As such, literal phrase-matching fails because of non-stem mismatches. Instead, we
tokenize the query and group it into subphrases of 1-3 words (where possible) and match
the phrases using fuzzed SEQUENCE queries instead.

The results are scored by the UPoH to try to eliminate excess-length matches (e.g. hits
with additional descriptors on top of the queried phrase) and bad fuzz matches (e.g. 
'pear' for 'peach'). 

This is accomplished by a combination of boosts for character- and word matches, penalties
for edit distance (using Levenshtein metric) and heavy score adjustments for perfect matches
and obvious mismatches.


## Testing:

An (extremely) non-exhaustive assortment of unit-, functional and load tests have been
included.

#### unit-testing:

COMMAND: `python -m pytest tests/unit`

INVOKE: `beemgmt unit-test` 

----

#### functional testing:

NOTE: **REQUIRES a running API!**

COMMAND: `python -m pytest tests/functional`

INVOKE: `beemgmt functional-test` 

----

#### load testing:

NOTE: **REQUIRES a running API!**

COMMAND: `locust -f tests\load\load.py --host http://localhost:8080 --headless --users <max users> --run-time <run time>`

INVOKE: `beemgmt load-test` 