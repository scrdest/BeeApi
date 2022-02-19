import functools
from copy import deepcopy

from beeapi.core.exceptions import ImpossibleException


class Trie:
    DEFAULT_MAX_DEPTH = 3
    DEFAULT_INPLACE = True

    def __init__(self, maxdepth: int = None, inplace_mode: bool = None):
        self.inplace_mode = self.DEFAULT_INPLACE if inplace_mode is None else bool(inplace_mode)
        self.maxdepth = int(self.DEFAULT_MAX_DEPTH if maxdepth is None else maxdepth)
        self.entries = 0
        self.data = dict()

        if self.maxdepth < 0:
            raise ValueError("Trie max depth must be a non-negative integer!")


    def __repr__(self):
        return str(self.data)


    def __len__(self):
        return self.entries


    @classmethod
    @functools.lru_cache(maxsize=50)
    def normalize_item(cls, item: str, *args, **kwargs):
        result = item.lower()
        return result


    def insert(self, item, in_place=None):
        _maxdepth = self.maxdepth

        inplace_mode = bool(self.inplace_mode) if in_place is None else bool(in_place)
        local_data = self.data if inplace_mode else deepcopy(self.data)
        new_entries = self.entries

        string = self.normalize_item(item=item)
        wordlen = len(string) - 1

        lens = local_data

        try:
            for (idx, letter) in enumerate(string):

                if idx < wordlen and idx < _maxdepth:
                    # Simple branch case; deepening
                    current_data = lens.setdefault(letter, dict())
                    if isinstance(current_data, dict):
                        new_lens = current_data
                        lens = new_lens

                elif idx < _maxdepth:
                    # Hit end of the word with no followup letters;
                    # IOW we need to deal with potential branches
                    current_data = lens.get(letter, dict())
                    if string not in current_data:
                        current_data.setdefault(None, list()).append(string)

                    lens[letter] = current_data
                    new_entries += 1
                    break

                elif idx < wordlen or idx == _maxdepth:
                    # Simple leaf case
                    current_data = lens.get(letter, list())
                    if string not in current_data:
                        current_data.append(string)

                    lens[letter] = current_data
                    new_entries += 1
                    break


        except ImpossibleException:
            raise

        else:
            if in_place:
                self.data = local_data
                self.entries = new_entries
                return self.data

            else:
                new_trie = self.from_trie_data(
                    data=local_data,
                    entries=new_entries
                )
                return new_trie


    def insert_batch(self, strings, in_place=None):
        _inplace = self.inplace_mode if in_place is None else bool(in_place)
        for string in strings:
            self.insert(string, in_place=_inplace)


    @classmethod
    def from_iterable(cls, strings, maxdepth=None, in_place=None):
        new_inst = cls(maxdepth=maxdepth, inplace_mode=in_place)
        # We always do in-place here since we're constructing a new instance:
        new_inst.insert_batch(strings=strings, in_place=True)
        return new_inst


    @classmethod
    def from_trie_data(cls, data, entries, maxdepth=None, in_place=None):
        new_inst = cls(maxdepth=maxdepth, inplace_mode=in_place)
        new_inst.data.update(data)
        new_inst.entries = entries
        return new_inst


    def __contains__(self, item):
        normalized_item = self.normalize_item(item=item)
        prefix_matches = self.get_prefix_matches(item=normalized_item)
        return normalized_item in prefix_matches


    def __getitem__(self, item):
        return self.get_prefix_matches(item=item)


    def get_prefix_matches(self, item):
        _maxdepth = self.maxdepth
        recursion_depth = _maxdepth - 1

        in_place = self.inplace_mode
        lens = self.data if in_place else deepcopy(self.data)

        string = self.normalize_item(item=item)
        wordlen = len(string)
        curr_depth = 0

        for (idx, letter) in enumerate(string):
            curr_depth = idx
            if curr_depth < _maxdepth and curr_depth < wordlen:
                try:
                    new_lens = lens[letter]

                except KeyError:
                    return list()

                else:
                    lens = new_lens

            else:
                new_lens = lens[letter]
                lens = new_lens
                break

        result = lens

        if curr_depth < _maxdepth:
            subtrees = list(lens.values())

            while curr_depth < recursion_depth:
                subtrees = sum([list(sub.values()) for sub in subtrees], [])
                curr_depth += 1

            else:
                subtrees = sum(subtrees, [])

            result = subtrees

        return result
