import re
import functools
import itertools

from whoosh import query
from whoosh.support.levenshtein import levenshtein

from beeapi import constants as beeconstants
from beeapi.core.parsing import OFFCategoriesDictParser, parse_query


def _run_phrase_query_uncached(word_tuple, searcher):
    terms = [
        query.Prefix(beeconstants.CONTENTS_COLUMN, word)
        for word in word_tuple
    ]

    sub_qry = query.Sequence(
        terms
    )

    submatches = searcher.search(
        sub_qry,
        limit=25
    )

    return submatches


_run_phrase_query_cached = functools.lru_cache(maxsize=beeconstants.PHRASE_QUERY_CACHE_SIZE)(_run_phrase_query_uncached)


def run_phrase_query(word_tuple, searcher, clear_cache=False, clear_on_cache_miss=True):
    if clear_cache:
        _run_phrase_query_cached.cache_clear()

    submatches = _run_phrase_query_cached(
        word_tuple,
        searcher
    )

    if clear_on_cache_miss and not submatches:
        _run_phrase_query_cached.cache_clear()

    return submatches


def evaluate_candidate(candidate, word_tuple, subphrases, user_query):
    # Welcome to the Most Unholy Pile of Heuristics!

    if candidate in user_query:
        # Direct match - best possible, heavy boost
        return candidate, (len(word_tuple) ** 2) * beeconstants.MAGIC_DIRECT_MATCH_BOOST

    candidate_words = candidate.split()
    word_tup_len = len(word_tuple)

    if len(candidate_words) != word_tup_len:
        # If match is longer (word-wise), can't possibly fully match
        return None, float("-inf")

    regex = "{term}\w*?\W*" if word_tup_len > 1 else "{term}\w?\w?"
    regex_match = re.search(
        "\s+".join(
            regex.format(term=term) for term in word_tuple
        ),
        user_query
    )

    if not regex_match:
        # The phrase must (fuzzy-)match the input (mostly,
        # to avoid making up new phrases not in query, but
        # also to limit excessive matching for single-terms)
        return None, float("-inf")

    phrase_match_score = 0
    word_match_score = 0
    pos_match_score = 0

    # Boost each direct word/pos match in a phrase
    phrase_match_score += sum(
        (w1 == w2 for (w1, w2) in itertools.zip_longest(
            user_query,
            candidate,
            fillvalue="*"
        ))
    ) * beeconstants.MAGIC_SENTENCE_MATCH_BOOST_MULT

    # Penalize mismatches (by min(levenshtein), because that's the best-case mismatch)
    try:
        phrase_match_score -= min(
            (levenshtein(candidate, subphrase) for subphrase in subphrases)
        ) * beeconstants.MAGIC_SENTENCE_MISMATCH_PENALTY_MULT
    except ValueError:
        raise ValueError((subphrases, candidate, word_tuple))


    # Character-wise scoring:
    for (qry_word, cand_word) in itertools.zip_longest(word_tuple, candidate_words):
        # Boost matching characters
        word_match_score += sum(
            (w1 == w2 for (w1, w2) in itertools.zip_longest(qry_word, cand_word, fillvalue="*"))
        ) * beeconstants.MAGIC_WORD_ALIGNMENT_BOOST_MULT

        # Penalize edits
        word_match_score -= (
                levenshtein(qry_word, cand_word)
                * beeconstants.MAGIC_WORD_ALIGNMENT_DIFF_PENALTY_MULT
        )


    # Add 'em up...
    total_score = sum((
        phrase_match_score,
        word_match_score,
        pos_match_score,
    ))

    return candidate, total_score


def evaluate_candidates(candidates, word_tuple, subphrases, user_query):
    best_cand, best_score = None, float("-inf")

    for candidate_match in candidates:
        cand_guess, cand_score = evaluate_candidate(
            candidate=candidate_match,
            word_tuple=word_tuple,
            subphrases=subphrases,
            user_query=user_query
        )

        if cand_score > best_score:
            best_cand, best_score = cand_guess, cand_score

    return best_cand, best_score


def run_query_uncached(user_query, searcher):
    normalized_query = user_query.lower()
    query_terms = parse_query(normalized_query)
    if not query_terms:
        return {}

    standardized_query_phrase = " ".join(query_terms)

    phrase_gen = itertools.chain.from_iterable((
        itertools.combinations(query_terms, n)
        for n in range(3, 0, -1)
    ))

    best_candidates = {}

    for word_tuple in phrase_gen:

        matches = run_phrase_query(word_tuple, searcher)
        if matches:
            candidates = (
                candidate_match[beeconstants.RAW_COLUMN]
                for candidate_match in matches
            )

            applicable_subphrases = {
                c for c in itertools.combinations(query_terms, len(word_tuple))
                if " ".join(c) in standardized_query_phrase
            }

            best_cand, best_score = evaluate_candidates(
                candidates=candidates,
                word_tuple=word_tuple,
                subphrases=applicable_subphrases,
                user_query=standardized_query_phrase,
            )

            if best_cand and best_score > 0:
                curr_score, _ = best_candidates.setdefault(best_cand, (best_score, word_tuple))
                if best_score > curr_score:
                    best_candidates[best_cand] = (best_score, word_tuple)

    return best_candidates


run_query_cached = functools.lru_cache(maxsize=beeconstants.USER_QUERY_CACHE_SIZE)(run_query_uncached)


def run_query(user_query, clear_cache=False, clear_on_cache_miss=True, index=None, dict_path=None):
    _index = index or OFFCategoriesDictParser.parse_cached(
        filepath=dict_path or beeconstants.DEFAULT_DICT_PATH
    )

    if clear_cache:
        run_query_cached.cache_clear()

    with _index.searcher() as searcher:
        scored_matches = run_query_cached(
            user_query=user_query,
            searcher=searcher
        )

    if clear_on_cache_miss and not scored_matches:
        run_query_cached.cache_clear()

    best_matches = list(scored_matches.keys())
    return best_matches

