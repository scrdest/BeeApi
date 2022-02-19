import abc


class BaseStemmer(abc.ABC):

    @abc.abstractmethod
    def stem(self, string: str, *args, **kwargs) -> str:
        return string


    def __call__(self, string, *args, **kwargs):
        result = self.stem(string, *args, **kwargs)
        return result