import abc
import functools
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
    DEFAULT_TRIE_DEPTH = 5


    @classmethod
    def _handle_line(cls, bin_line: bytes, lineno: int):
        
        safe_length = (cls.DATA_COLUMN_INDEX + 1)
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

        return normalized_words


    @classmethod
    def _read_data(cls, filepath):
        with open(filepath, "rb") as data:
            for (lineno, bin_line) in enumerate(data):
                if lineno == 0:
                    continue

                yield bin_line, lineno


    @classmethod
    def index_data(cls, processed_line: str):
        return processed_line


    @classmethod
    def parse(cls, filepath, trie_max_depth=None, *args, **kwargs):
        new_trie = Trie(maxdepth=trie_max_depth)

        raw_data_stream = cls._read_data(
            filepath=filepath
        )

        for (bin_line, lineno) in raw_data_stream:
            processed_line = cls._handle_line(bin_line=bin_line, lineno=lineno)
            cls.index_data(processed_line=processed_line)

        return new_trie


    @classmethod
    @functools.lru_cache(maxsize=1)
    def parse_cached(cls, filepath, trie_max_depth=None, *args, **kwargs):
        result = cls.parse(
            filepath=filepath,
            trie_max_depth=trie_max_depth,
            *args,
            **kwargs
        )
        return result
