import logging

from sanic import json, Sanic
from sanic.views import HTTPMethodView

from work.npc.ai.chatbot.api.Persona import Personas
from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


class PersonaHandler(HTTPMethodView):

    @classmethod
    def error(cls, message):
        response = {"error": message}
        return json(response, status=400, content_type='application/json')

    __modelTranslation = {
        "bb2-400M": "facebook/blenderbot-400M-distill",
        "bb2-1B": "facebook/blenderbot-1B-distill",
        "bb2-3B": "zoo:blender/blender_3B/model",
    }

    async def post(self, request):

        payload = request.json
        logging.info(f"POST: {payload}")

        sanic = Sanic.get_app()

        botModel = payload.get("model", sanic.config.get("botModel", "bb2-1B"))
        if botModel in self.__modelTranslation:
            botModel = self.__modelTranslation[botModel]

        logging.info(f"Use model {botModel}")

        name = payload.get("name", "Bot")
        botPersona = payload.get("persona", [])

        bot = TransformerBot.of(botPersona, modelName=botModel) or ParlaiBot.of(botPersona, modelName=botModel)
        if bot is None:
            return self.error(f"Unknown chat bot model {botModel}")

        persona = Personas.new(bot, name=name)

        response = {
            "version": sanic.config.VERSION,
            "persona": str(persona.id),
            "name": persona.name,
            "model": botModel,
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')

    async def get(self, request, personaId):
        payload = request.json
        logging.info(f"GET: {personaId}: {payload}")

        persona = Personas.get(personaId)
        if not persona:
            return self.error(f"persona {personaId} not found")

        sanic = Sanic.get_app()

        response = {
            "version": sanic.config.VERSION,
            "persona": str(persona.id),
            "name": persona.name,
            "facts": list(persona.getPersona()),
        }

        logging.info(response)

    async def delete(self, request, personaId):
        payload = request.json
        logging.info(f"DELETE: {personaId} {payload}")

        status = 200 if Personas.delete(personaId) else 202
        return json({}, status=status, content_type='application/json')