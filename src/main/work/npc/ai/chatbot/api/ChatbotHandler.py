import logging

from bson import ObjectId
from sanic import json, Sanic
from sanic.views import HTTPMethodView


class ChatbotHandler(HTTPMethodView):

    ALLOWS_ATTACHMENT = ["chat", "note"]

    @classmethod
    def error(cls, message):
        response = {"error": message}
        return json(response, status=400, content_type='application/json')

    def post(self, request):

        payload = request.json
        logging.info(f"POST: {payload}")

        transactionId = payload.get("transactionId", str(ObjectId()))
        userId = payload.get("userId", None)

        sanic = Sanic.get_app()

        response = {
            "version": sanic.config.VERSION,
            "transactionId": transactionId,
            "userId": userId,
        }

        logging.info(response)

        return json(response, status=200, content_type='application/json')

