from cj.chatbot.rules.Action import Action
from cj.chatbot.rules.Dao import Dao


class EstablishDao(Action):
    def __init__(self, daoId: str):
        self.dao = Dao.of(daoId)

    def act(self, userId: str = None):
        self.dao.establish()

    def getProperties(self) -> dict:
        return self.dao.getProperties()
