from abc import ABC, abstractmethod


class Bot(ABC):

    @classmethod
    def useModel(cls, modelName: str):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def respondTo(self, utterance: str, **kwargs):
        pass
