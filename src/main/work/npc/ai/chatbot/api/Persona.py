import logging
import time
from typing import Optional, Iterator, Dict, List

import bson

from work.npc.ai.chatbot.bots.Bot import Bot


class Persona:
    def __init__(self, bot: Bot, name: str):
        self.id = bson.ObjectId()
        self.name = name
        self.bot = bot
        self.lastAccess = time.time()

    def getConversation(self, withEnum=None) -> Iterator[str]:
        for idx, utterance in enumerate(self.bot.getConversation()):
            enum = f"{idx:-3}. " if withEnum else ""
            yield f"{enum}{utterance}"

    def getPersona(self) -> List[str]:
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
        toDie = []
        for personaId in cls.personas.keys():
            if cls.personas[personaId].lastAccess + duration < now:
                toDie.append(personaId)

        if toDie:
            for personaId in toDie:
                persona = cls.personas.pop(personaId)
                logging.info(f"Persona {persona.name} {personaId} killed.")

    @classmethod
    def get(cls, personaId: str) -> Optional[Persona]:
        persona = cls.personas.get(personaId, None)
        if persona:
            persona.lastAccess = time.time()
        return persona

    @classmethod
    def delete(cls, personaId: str) -> Optional[Persona]:
        return cls.personas.pop(personaId) if personaId in cls.personas else None
