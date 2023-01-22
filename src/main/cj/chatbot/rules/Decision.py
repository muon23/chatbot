from abc import ABC, abstractmethod


class Decision(ABC):

    @abstractmethod
    def decide(self, userId: str = None) -> bool:
        pass

    @abstractmethod
    def getProperties(self) -> dict:
        pass
