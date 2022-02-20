from beeapi.api.app import get_app
from beeapi.core.parsing import OFFCategoriesDictParser, DICT_PATH
from beeapi.core.stemming import NltkStemmer

app = get_app()


@app.get("/")
async def root():
    return {"message": "Hello!"}


@app.post("/jobs")
async def new_job(q):
    query = q
    stemmed_query = NltkStemmer.get_stemmer_for(lang="english").stem(query)
    dictionary = OFFCategoriesDictParser.parse_cached(
        filepath=DICT_PATH,
        trie_max_depth=5
    )
    is_match = stemmed_query in dictionary
    matches = []

    if is_match:
        matches.append(query)

    msg = {
        "matches": matches
    }
    return msg

