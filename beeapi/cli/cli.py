import os

from beeapi import constants as beeconsts
from beeapi.core.queryhandler import run_query


def get_query_input():
    raw_query = input("Enter text to search: ")
    return raw_query


def run_app_once(raw_query, clear_cache=False):
    match_phrases = run_query(
        user_query=raw_query,
        clear_cache=clear_cache
    )
    return match_phrases


def run_app(_clear_cache=False):
    running = True
    clear_cache = _clear_cache or False

    while running:
        raw_query = get_query_input()

        if raw_query == "\\q":
            break

        if raw_query == "\\c":
            clear_cache = True
            print("Cache will be cleared.")
            continue

        match_phrases = run_app_once(
            raw_query=raw_query,
            clear_cache=clear_cache
        )

        clear_cache = False
        print(match_phrases)

    else:
        print("Quitting...")


def run_default_mode():
    run_loop = (os.environ.get(beeconsts.ENV_MAIN_RUN_LOOPED) or '').strip().lower() == 'true'

    if run_loop:
        run_app()

    else:
        query = get_query_input()
        result = run_app_once(
            raw_query=query
        )
        print(result)

    return True


if __name__ == '__main__':
    run_default_mode()
