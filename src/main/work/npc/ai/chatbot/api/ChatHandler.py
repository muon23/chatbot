import logging

from sanic import json, Sanic
from sanic.views import HTTPMethodView

from work.npc.ai.chatbot.api.Persona import Personas


class ChatHandler(HTTPMethodView):

    @classmethod
    def error(cls, message, code=400):
        response = {"error": message}
        return json(response, status=code, content_type='application/json')

    async def post(self, request, personaId):

        payload = request.json
        logging.info(f"POST: {personaId}: {payload}")

        utterance = payload.get("utterance", "")

        persona = Personas.get(personaId)
        if not persona:
            return self.error(f"persona {personaId} not found")

        sanic = Sanic.get_app()

        persona.bot.modifyConversation(payload)
        reply = persona.bot.respondTo(utterance, debug=sanic.config.get("debug", None))

        if not reply:
            return self.error("Service temporarily unavailable", 503)

        response = {
            "version": sanic.config.VERSION,
            "persona": str(persona.id),
            "name": persona.name,
            "reply": reply,
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')

    async def get(self, request, personaId):
        args = request.args
        logging.info(f"GET: {personaId}: {args}")

        persona = Personas.get(personaId)
        if not persona:
            return self.error(f"persona {personaId} not found")

        withEnum = args.get("enumerate", None)

        sanic = Sanic.get_app()

        response = {
            "version": sanic.config.VERSION,
            "persona": str(persona.id),
            "name": persona.name,
            "model": persona.bot.getModelName(),
            "conversation": list(persona.getConversation(withEnum=withEnum)),
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')
