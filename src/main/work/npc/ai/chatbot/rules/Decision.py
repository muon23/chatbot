from abc import ABC, abstractmethod

from work.npc.ai.chatbot.rules.Dao import Dao


class Decision(ABC):
    @abstractmethod
    def decide(self, dao: Dao) -> bool:
        pass
