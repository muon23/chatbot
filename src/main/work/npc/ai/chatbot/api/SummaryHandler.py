import logging

from sanic import json, Sanic
from sanic.views import HTTPMethodView

from work.npc.ai.chatbot.summary.Gpt3Summarizer import Gpt3Summarizer


class SummaryHandler(HTTPMethodView):

    @classmethod
    def error(cls, message):
        response = {"error": message}
        return json(response, status=400, content_type='application/json')

    async def post(self, request):
        payload = request.json
        logging.info(f"POST: {payload}")

        model = payload.get("model", "gpt3")
        text = payload.get("text", "")
        mode = payload.get("mode", "summary")
        numTitles = payload.get("numTitles", 3)
        language = payload.get("language", None)

        sanic = Sanic.get_app()

        try:
            summarizer = (
                Gpt3Summarizer.of(model)
            )
            if summarizer is None:
                return self.error(f"Unknown chat bot model {model}")

            summary = summarizer.summarize(text, mode=mode, numTitles=numTitles, language=language)

            response = {
                "version": sanic.config.VERSION,
                mode: summary,
            }

            if language:
                response["language"] = language

            logging.info(response)

        except RuntimeError as e:
            logging.warning(str(e))
            return self.error(str(e))

        return json(response, status=200, content_type='application/json')


