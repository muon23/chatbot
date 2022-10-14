from abc import ABC, abstractmethod
from typing import TypeVar, Iterator, Tuple


class Bot(ABC):
    Bot = TypeVar("Bot")

    @classmethod
    def useModel(cls, modelName: str):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def respondTo(self, utterance: str, **kwargs):
        pass

    @abstractmethod
    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        pass

    @abstractmethod
    def getPersona(self) -> str:
        pass

