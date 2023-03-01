import logging
import json as pjson
import os

from sanic import json, Sanic
from sanic.views import HTTPMethodView

from cj.chatbot.api.Persona import Personas
from cj.chatbot.bots.Gpt3Bot import Gpt3Bot
# from cj.chatbot.bots.ParlaiBot import ParlaiBot
from cj.chatbot.bots.TransformerBot import TransformerBot


class PersonaHandler(HTTPMethodView):

    @classmethod
    def error(cls, message):
        response = {"error": message}
        return json(response, status=400, content_type='application/json')

    __modelTranslation = {
        "bb2-400M": "facebook/blenderbot-400M-distill",
        "bb2-1B": "facebook/blenderbot-1B-distill",
        # "bb2-3B": "zoo:blender/blender_3B/model",
        "bb2-3B": "facebook/blenderbot-3B",
        "gpt-3": "gpt3",
    }

    async def post(self, request):

        payload = request.json
        logging.info(f"POST: {payload}")

        sanic = Sanic.get_app()

        load = payload.get("load", None)
        if load:
            load = os.path.expanduser(load)
            try:
                with open(load, 'r') as f:
                    data = pjson.load(f)
                    payload = data["persona"]  # Override payload with whatever in the file
            except FileNotFoundError:
                return self.error(f"File {load} not found")
            except KeyError:
                return self.error(f"File {load} has incompatible format")

        botModel = payload.get("model", sanic.config.get("botModel", "gpt3"))
        if botModel in self.__modelTranslation:
            botModel = self.__modelTranslation[botModel]

        logging.info(f"Use model {botModel}")

        botPersona = payload.pop("persona", [])

        try:
            bot = (
                    TransformerBot.of(botPersona, modelName=botModel, **payload) or
                    # ParlaiBot.of(botPersona, modelName=botModel, **payload) or
                    Gpt3Bot.of(botPersona, modelName=botModel, **payload)
            )
            if bot is None:
                return self.error(f"Unknown chat bot model {botModel}")

        except RuntimeError as e:
            logging.warning(str(e))
            return self.error(str(e))

        persona = Personas.new(bot, name=payload.get("name", "Bot"))

        if load:
            await persona.bot.load(data["script"])

        response = {
            "version": sanic.config.VERSION,
            "persona": str(persona.id),
            "name": persona.name,
            "model": botModel,
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')

    async def get(self, request, personaId):
        if not personaId:
            self.error("Missing personal ID")

        payload = request.json
        logging.info(f"GET: {personaId}: {payload}")

        persona = Personas.get(personaId)
        if not persona:
            return self.error(f"persona {personaId} not found")

        sanic = Sanic.get_app()

        response = {
            "version": sanic.config.VERSION,
            "name": persona.name,
            "persona": list(persona.getPersona()),
            "model": persona.bot.getModelName(),
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')

    async def delete(self, request, personaId):
        payload = request.json
        logging.info(f"DELETE: {personaId} {payload}")

        status = 200 if Personas.delete(personaId) else 202
        return json({}, status=status, content_type='application/json')
