import logging

import beeapi.constants

loggers = {}


def get_logger(name=None):
    _name = name or beeapi.constants.DEFAULT_LOGGER_NAME
    cached_logger = loggers.get(_name)

    if cached_logger:
        return cached_logger

    stream_handler = logging.StreamHandler()

    new_logger = logging.getLogger(name=_name)
    new_logger.setLevel(logging.INFO)
    new_logger.addHandler(stream_handler)

    loggers[_name] = new_logger

    return new_logger

