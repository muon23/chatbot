from work.npc.ai.chatbot.rules.Action import Action
from work.npc.ai.chatbot.rules.Dao import Dao


class EstablishDao(Action):
    def __init__(self, daoId: str):
        self.dao = Dao.of(daoId)

    def act(self, userId: str = None):
        self.dao.establish()

    def getProperties(self) -> dict:
        return self.dao.getProperties()
