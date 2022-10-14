from typing import List, Iterator, Tuple

from parlai.core.agents import create_agent_from_model_file

from work.npc.ai.chatbot.bots.Bot import Bot


class ParlaiBot(Bot):
    agent = None

    __DEFAULT_MODEL = "zoo:blender/blender_3B/model"

    @classmethod
    def of(cls, persona: List[str] = None, modelName=__DEFAULT_MODEL) -> Bot:
        return ParlaiBot(persona, modelName) if modelName in [
            "zoo:blender/blender_400M/model",
            "zoo:blender/blender_3B/mode",
            "zoo:bb3/bb3_3B/model",
            cls.__DEFAULT_MODEL
        ] else None

    @classmethod
    def useModel(cls, modelName):
        cls.agent = create_agent_from_model_file(modelName)

    def __init__(self, persona: List[str] = None, modelName=__DEFAULT_MODEL):
        if not self.agent:
            self.useModel(modelName)

        self.persona = persona if persona else []
        self.reset()

    def reset(self):
        facts = ""

        for fact in self.persona:
            facts = facts + f"your persona: {fact}\n"

        self.agent.observe({'text': facts, 'episode_done': False})

    def respondTo(self, utterance: str, show=False):
        if show:
            print(f">> {utterance}")

        self.agent.observe({'text': utterance, 'episode_done': False})
        response = self.agent.act()

        return response['text']

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        fromUser = True
        for utterance in self.agent.history.history_strings[1:]:
            yield fromUser, utterance
            fromUser = not fromUser

    def getPersona(self) -> str:
        return self.agent.history.history_strings[0]