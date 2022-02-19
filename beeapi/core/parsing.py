import abc
import re

from beeapi.core.stemming import NltkStemmer
from beeapi.core.trie import Trie

DICT_PATH = r"C:\Users\scrdest\PycharmProjects\StreetBeesAssignment1\spec\off_categories.tsv"
wordmatcher = re.compile("(.*?:)?(.*?)$")


class BaseDataDictParser(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse(cls, filepath, *args, **kwargs):
        return None

    def __call__(self, filepath, *args, **kwargs):
        return self.parse(filepath, *args, **kwargs)


class OFFCategoriesDictParser(BaseDataDictParser):
    DATA_COLUMN_INDEX = 1

    @classmethod
    def parse(cls, filepath, trie_max_depth=5, *args, **kwargs):
        new_trie = Trie(maxdepth=trie_max_depth)
        safe_length = (cls.DATA_COLUMN_INDEX + 1)

        with open(DICT_PATH, "rb") as data:
            for (lineno, bin_line) in enumerate(data):
                if lineno == 0:
                    continue

                line = bin_line.decode("utf8")

                columns = line.split("\t")
                if len(columns) < safe_length:
                    print(f"Skipping line {lineno} - insufficient columns!")

                raw_data = columns[cls.DATA_COLUMN_INDEX]

                deprefixer_match = wordmatcher.fullmatch(raw_data)
                if not deprefixer_match:
                    print(f"Skipping line {lineno} due to lack of prefix match!")

                deprefixed_data = deprefixer_match.group(2)
                if not deprefixed_data:
                    print(f"Skipping line {lineno} due to lack of words!")

                lang_prefix = deprefixer_match.group(1)

                data_words = deprefixed_data.split("-")
                lowercased_words = (word.lower() for word in data_words)

                stemmer = NltkStemmer.get_stemmer_for(lang_prefix[:-1] if lang_prefix else None)
                stemmed_words = (stemmer(word) for word in lowercased_words)

                normalized_words = " ".join(stemmed_words)

                # print(
                #     lineno,
                #     f"prefix: `{lang_prefix[:-1] if lang_prefix else ''}`",
                #     normalized_words,
                #     sep=" - "
                # )

                new_trie.insert(normalized_words, in_place=True)

        return new_trie


