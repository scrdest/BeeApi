import functools

from nltk.stem import SnowballStemmer

from beeapi.core.abcs import BaseStemmer


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
