from beeapi.core.parsing import OFFCategoriesDictParser, DICT_PATH
from beeapi.core.stemming import NltkStemmer


def run_app():
    dictionary = OFFCategoriesDictParser.parse_cached(
        filepath=DICT_PATH
    )
    running = True
    while running:
        query = input("Enter text to search: ")
        stemmed_query = NltkStemmer.get_stemmer_for(lang="english").stem(query)
        matches = stemmed_query in dictionary
        print(matches)
        break


run_app()
