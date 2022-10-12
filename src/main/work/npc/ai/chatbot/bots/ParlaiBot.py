from typing import List

from parlai.core.agents import create_agent_from_model_file

from work.npc.ai.chatbot.bots.Bot import Bot


class ParlaiBot(Bot):
    agent = None

    __DEFAULT_MODEL = "zoo:blender/blender_3B/model"

    @classmethod
    def useModel(cls, modelName):
        cls.agent = create_agent_from_model_file(modelName)

    def __init__(self, name: str, persona: List[str] = None, modelName=__DEFAULT_MODEL):
        if not self.agent:
            self.useModel(modelName)

        self.name = name
        self.persona = persona
        self.reset()

    def reset(self):
        facts = f"your persona: My name is {self.name}.  "

        for fact in self.persona:
            facts = facts + f"\nyour persona: {fact}"

        self.agent.observe({'text': facts, 'episode_done': False})

    def respondTo(self, utterance: str, show=False):
        if show:
            print(f">> {utterance}")

        self.agent.observe({'text': utterance, 'episode_done': False})
        response = self.agent.act()

        return response['text']
