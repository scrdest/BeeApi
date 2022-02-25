from whoosh.fields import SchemaClass, TEXT, ID, NUMERIC

from beeapi.core.analyzers import BeeAnalyzer


class OFFDictSchema(SchemaClass):
    path = ID(stored=True, unique=True)
    lineno = NUMERIC(stored=True)
    original = TEXT(stored=True)
    contents = TEXT(analyzer=BeeAnalyzer)
    stemmed = TEXT(analyzer=BeeAnalyzer)
