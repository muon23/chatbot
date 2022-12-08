from abc import ABC, abstractmethod
from typing import TypeVar, Iterator, Optional


class Bot(ABC):
    Bot = TypeVar("Bot")

    def __init__(self, name: str = "Bot"):
        self.name = name

    @abstractmethod
    def modifyConversation(self, instruction, **kwargs):
        pass

    @abstractmethod
    async def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def getConversation(self) -> Iterator[str]:
        pass

    @abstractmethod
    def getPersona(self) -> str:
        pass

    @abstractmethod
    def getModelName(self) -> str:
        pass
