from abc import ABC, abstractmethod

from work.npc.ai.chatbot.rules.Dao import Dao


class Action(ABC):
    @abstractmethod
    def act(self, dao: Dao):
        pass
