import functools

from beeapi.core.abcs import BaseStemmer
from beeapi.core.logging import get_logger

logger = get_logger()


NLTK_UNAVAILABLE, NLTK_ERR = True, None

try:
    from nltk.stem import SnowballStemmer
except ImportError as nltk_import_err:
    from beeapi.core.abcs import BaseStemmer as SnowballStemmer
    NLTK_ERR = nltk_import_err
else:
    NLTK_UNAVAILABLE = False


class BasicStemmer(BaseStemmer):
    def stem(self, string: str, *args, **kwargs) -> str:
        preprocessed = super().stem(string, *args, **kwargs)
        processed = preprocessed.lower()
        return processed


class NltkStemmer(BaseStemmer):
    DEFAULT_LANG = "english"

    language_lookup = {
        None: DEFAULT_LANG,
        "ar": "arabic",
        "da": "danish",
        "de": "german",
        "en": "english",
        "es": "spanish",
        "fi": "finnish",
        "fr": "french",
        "hu": "hungarian",
        "it": "italian",
        "nl": "dutch",
        "pt": "portuguese",
        "ro": "romanian",
        "ru": "russian",
        "sk": "swedish",
    }

    def __init__(self, language):
        if NLTK_UNAVAILABLE:
            logger.warning("The NLTK library required to use this class is not available!", exc_info=True)
            raise NLTK_ERR

        self.nltk = SnowballStemmer(
            language=language
        )

    def stem(self, string: str, *args, **kwargs) -> str:
        preprocessed = super().stem(string, *args, **kwargs)
        processed = self.nltk.stem(preprocessed)
        return processed


    @classmethod
    @functools.lru_cache(maxsize=5)
    def get_stemmer_for(cls, lang: str = None):
        language = cls.language_lookup.get(lang)

        if language is None:
            # If it's None at this point, it's not a Snowball-stemmable language
            stemmer = BasicStemmer()

        else:
            stemmer = NltkStemmer(language=language)

        return stemmer


class WhooshSnowballStemmer(BaseStemmer):
    from whoosh.lang.snowball import classes as snowball_classes

    def __init__(self, stemmer):
        self.stemmer = stemmer


    def stem(self, string: str, *args, **kwargs) -> str:
        processed = self.stemmer.stem(string)
        return processed


    @classmethod
    @functools.lru_cache(maxsize=5)
    def get_stemmer_for(cls, lang: str = None):
        language = lang or "en"
        stemmer_class = cls.snowball_classes.get(language)

        if stemmer_class is None:
            # If it's None at this point, it's not a Snowball-stemmable language
            stemmer = BasicStemmer()

        else:
            stemmer = stemmer_class()

        return cls(stemmer=stemmer)

