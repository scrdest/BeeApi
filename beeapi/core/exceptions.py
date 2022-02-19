class ImpossibleException(BaseException):
    """An exception that should never actually be raised.
    Exists purely for try/except/else clauses with no handling for errors
    """

    def __init__(self):
        raise RuntimeError("This exception should never be raised - it's only a syntactic placeholder!")
