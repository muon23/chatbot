from abc import ABC, abstractmethod
from typing import TypeVar, Iterator, Tuple, Optional, Union


class Bot(ABC):
    Bot = TypeVar("Bot")

    @abstractmethod
    def modifyConversation(self, instruction, **kwargs):
        pass

    @abstractmethod
    def respondTo(self, utterance: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        pass

    @abstractmethod
    def getConversation(self) -> Iterator[Tuple[Union[bool, str], str]]:
        pass

    @abstractmethod
    def getPersona(self) -> str:
        pass

    @abstractmethod
    def getModelName(self) -> str:
        pass
