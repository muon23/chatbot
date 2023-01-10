from work.npc.ai.chatbot.rules.Dao import Dao


class User:
    @classmethod
    def of(cls, daoId: str) -> "User":
        pass

    def agreedToConsensus(self, doa: Dao) -> bool:
        pass
