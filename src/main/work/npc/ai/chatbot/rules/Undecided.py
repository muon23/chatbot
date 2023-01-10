from work.npc.ai.chatbot.rules.Decision import Decision


class Undecided(Decision):
    def decide(self, userId: str = None) -> bool:
        return False
