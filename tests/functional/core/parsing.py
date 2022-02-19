from beeapi.core.parsing import DICT_PATH, OFFCategoriesDictParser
from beeapi.core.stemming import NltkStemmer


def test_sample_dict():
    trie = OFFCategoriesDictParser.parse(filepath=DICT_PATH)
    print("New Trie: ")
    print(trie)
    raw_testwords = [("cauliflower cheese", "en")]
    testwords = [NltkStemmer.get_stemmer_for(lang).stem(word) for (word, lang) in raw_testwords]

    for word in testwords:
        print("{word} in Trie: {result}".format(word=word, result=word in trie))

