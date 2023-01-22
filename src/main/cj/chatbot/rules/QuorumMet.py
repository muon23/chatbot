from cj.chatbot.rules.Dao import Dao
from cj.chatbot.rules.Decision import Decision


class QuorumMet(Decision):
    def __init__(self, daoId: str):
        self.dao = Dao.of(daoId)

    def decide(self, userId: str = None) -> bool:
        return self.dao.getQuorumSize() <= self.dao.getNumMembers()

    def getProperties(self) -> dict:
        return self.dao.getProperties()
