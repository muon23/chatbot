from abc import ABC, abstractmethod
from typing import TypeVar, Iterator, Optional, List


class Bot(ABC):
    Bot = TypeVar("Bot")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Bot")

    @abstractmethod
    async def modifyConversation(self, instruction, **kwargs):
        pass

    @abstractmethod
    async def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def getConversation(self) -> Iterator[str]:
        pass

    @abstractmethod
    def getPersona(self) -> List[str]:
        pass

    @abstractmethod
    def getModelName(self) -> str:
        pass

    @abstractmethod
    async def load(self, script: List[str]):
        pass
