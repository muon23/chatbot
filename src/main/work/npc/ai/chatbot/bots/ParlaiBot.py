from typing import List, Iterator, Tuple, Optional

from parlai.core.agents import create_agent_from_model_file

from work.npc.ai.chatbot.bots.Bot import Bot


class ParlaiBot(Bot):

    __DEFAULT_MODEL = "zoo:blender/blender_3B/model"

    @classmethod
    def of(cls, persona: List[str] = None, modelName=__DEFAULT_MODEL) -> Bot:
        return ParlaiBot(persona, modelName) if modelName in [
            "zoo:blender/blender_400M/model",
            "zoo:blender/blender_3B/mode",
            "zoo:bb3/bb3_3B/model",
            cls.__DEFAULT_MODEL
        ] else None

    def __init__(self, persona: List[str] = None, modelName=__DEFAULT_MODEL):
        self.modelName = modelName
        self.agent = create_agent_from_model_file(modelName)
        self.persona = persona if persona else []
        self.modifyConversation()

    def modifyConversation(self, instruction=None, **kwargs):
        if not instruction or "reset" not in instruction:
            return

        facts = ""

        for fact in self.persona:
            facts = facts + f"your persona: {fact}\n"

        self.agent.observe({'text': facts, 'episode_done': False})

    def respondTo(self, utterance: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        self.agent.observe({'text': utterance, 'episode_done': False})
        response = self.agent.act()

        return response['text'], None

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        fromUser = True
        for utterance in self.agent.history.history_strings[1:]:
            yield fromUser, utterance
            fromUser = not fromUser

    def getPersona(self) -> str:
        return self.agent.history.history_strings[0]

    def getModelName(self) -> str:
        return self.modelName
