import functools

from whoosh import analysis
from whoosh.support.charset import accent_map


@functools.lru_cache(maxsize=1)
def build_analyzer():
    analyzer = (
        analysis.RegexTokenizer()
        | analysis.StripFilter()
        | analysis.LowercaseFilter()
        | analysis.CharsetFilter(accent_map)
    )

    return analyzer


BeeAnalyzer = build_analyzer()
