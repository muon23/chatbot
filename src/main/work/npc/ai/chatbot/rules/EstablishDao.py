from work.npc.ai.chatbot.rules.Action import Action
from work.npc.ai.chatbot.rules.Dao import Dao


class EstablishDao(Action):
    def act(self, dao: Dao):
        dao.establish()