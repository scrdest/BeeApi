import abc
import functools
import os
import re

from beeapi.core import apptypes, logging
from beeapi.core.indexing import build_file_storage, get_existing_index, build_file_indexer, add_document_to_index
from beeapi.core.stemming import WhooshSnowballStemmer

logger = logging.get_logger()
wordmatcher = re.compile("(.*?:)?(.*?)$")

QUERY_PARSER_PATTERN = re.compile(r"(\.?\w+)+")


class BaseDataDictParser(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse(cls, filepath, *args, **kwargs):
        return None

    def __call__(self, filepath, *args, **kwargs):
        return self.parse(filepath, *args, **kwargs)


class OFFCategoriesDictParser(BaseDataDictParser):
    DATA_COLUMN_INDEX = 1
    DEFAULT_WORKERS_COUNT = 1


    @classmethod
    def _handle_line(cls, bin_line: bytes, lineno: int) -> apptypes.PhrasePair:

        safe_length = (cls.DATA_COLUMN_INDEX + 1)
        line = bin_line.decode("utf8")

        columns = line.split("\t")
        if len(columns) < safe_length:
            logger.info(f"Skipping line {lineno} - insufficient columns!")

        raw_data = columns[cls.DATA_COLUMN_INDEX]

        deprefixer_match = wordmatcher.fullmatch(raw_data)
        if not deprefixer_match:
            logger.info(f"Skipping line {lineno} due to lack of prefix match!")

        deprefixed_data = deprefixer_match.group(2)
        if not deprefixed_data:
            logger.info(f"Skipping line {lineno} due to lack of words!")

        raw_lang_prefix = deprefixer_match.group(1)
        lang_prefix = raw_lang_prefix[:-1] if raw_lang_prefix else None

        data_words = deprefixed_data.split("-")
        lowercased_words = [word.lower() for word in data_words]

        stemmer = WhooshSnowballStemmer.get_stemmer_for(lang_prefix)
        stemmed_words = [stemmer(word) for word in lowercased_words]

        raw_joined_words = " ".join(lowercased_words)
        joined_words = " ".join(stemmed_words)

        return raw_joined_words, joined_words


    @classmethod
    def _handle_lines(
        cls,
        bin_line_stream: apptypes.AnnotatedRawDataStream
    ) -> apptypes.PhraseGen:

        for (bin_line, lineno) in bin_line_stream:
            raw_processed_line = cls._handle_line(bin_line=bin_line, lineno=lineno)
            yield raw_processed_line, lineno


    @classmethod
    def _read_data(cls, filepath: os.PathLike) -> apptypes.AnnotatedRawDataStream:

        with open(filepath, "rb") as data:
            for (lineno, bin_line) in enumerate(data):
                if lineno == 0:
                    # Skip header
                    continue

                yield bin_line, lineno


    @classmethod
    def _index_data(
        cls,
        processed_lines: apptypes.PhraseIter,
        workers: int = None
    ):

        _workers = workers or cls.DEFAULT_WORKERS_COUNT
        indexer = build_file_indexer()
        writer = indexer.writer(procs=_workers)

        for raw_processed_line, lineno in processed_lines:
            raw_line, stemmed_line = raw_processed_line
            add_document_to_index(
                writer=writer,
                original=raw_line,
                stemmed=stemmed_line,
                lineno=lineno,
                commit=False
            )

        writer.commit()

        return indexer


    @classmethod
    def parse(cls, filepath: os.PathLike, *args, **kwargs) -> apptypes.Index:
        raw_data_stream = cls._read_data(
            filepath=filepath
        )

        processed_data_stream = cls._handle_lines(
            bin_line_stream=raw_data_stream
        )

        indexer = cls._index_data(
            processed_lines=processed_data_stream
        )

        return indexer


    @classmethod
    @functools.lru_cache(maxsize=1)
    def parse_cached(cls, filepath: os.PathLike, *args, **kwargs) -> apptypes.Index:
        file_storage = build_file_storage()
        index = (
                get_existing_index(
                    storage=file_storage
                )
                or cls.parse(filepath, *args, **kwargs)
        )
        return index


def parse_query(user_query):
    terms = QUERY_PARSER_PATTERN.findall(user_query)
    return terms
