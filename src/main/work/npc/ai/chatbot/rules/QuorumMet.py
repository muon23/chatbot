from work.npc.ai.chatbot.rules.Dao import Dao
from work.npc.ai.chatbot.rules.Decision import Decision


class QuorumMet(Decision):
    def decide(self, dao: Dao) -> bool:
        return dao.getQuorumSize() <= dao.getNumMembers()
