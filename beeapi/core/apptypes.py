import typing

import whoosh.index

RawData = bytes
AnnotatedRawData = tuple[RawData, int]
AnnotatedRawDataStream = typing.Iterable[AnnotatedRawData]

Phrase = str
PhrasePair = tuple[Phrase, Phrase]
LangPhrase = tuple[str, Phrase]
AnnotatedPhrase = tuple[Phrase, int]
AnnotatedLangPhrase = tuple[LangPhrase, int]
PhraseIter = typing.Iterable[AnnotatedPhrase]
PhraseGen = typing.Iterable[AnnotatedPhrase]

Index = whoosh.index.Index
