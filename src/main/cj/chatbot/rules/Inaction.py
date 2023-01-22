from cj.chatbot.rules.Action import Action


class Inaction(Action):
    def getProperties(self) -> dict:
        pass

    def act(self, userId: str = None):
        pass
