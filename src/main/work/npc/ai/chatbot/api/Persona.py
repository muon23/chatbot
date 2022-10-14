import time
from typing import Optional, Iterator, Dict

import bson

from work.npc.ai.chatbot.bots.Bot import Bot


class Persona:
    def __init__(self, bot: Bot, name: str):
        self.id = bson.ObjectId()
        self.name = name
        self.bot = bot
        self.createdTime = time.time()

    def getConversation(self) -> Iterator[str]:
        for utterance in self.bot.getConversation():
            speaker = "You" if utterance[0] else self.name
            yield f"{speaker}: {utterance[1]}"

    def getPersona(self) -> str:
        return self.bot.getPersona()


class Personas:
    personas: Dict[str, Persona] = dict()

    @classmethod
    def new(cls, bot: Bot, name="Bot") -> Persona:
        persona = Persona(bot, name)
        cls.personas[str(persona.id)] = persona
        return persona

    @classmethod
    def purge(cls, duration: float):
        now = time.time()
        for personaId in cls.personas.keys():
            if cls.personas[personaId].createdTime + duration < now:
                cls.personas.pop(personaId)

    @classmethod
    def get(cls, personaId: str) -> Optional[Persona]:
        return cls.personas.get(personaId, None)

    @classmethod
    def delete(cls, personaId: str) -> Optional[Persona]:
        return cls.personas.pop(personaId) if personaId in cls.personas else None
