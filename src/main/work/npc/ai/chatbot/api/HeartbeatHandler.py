from sanic import json, Sanic
from sanic.views import HTTPMethodView

from work.npc.ai.chatbot.api.Persona import Personas


class HeartbeatHandler(HTTPMethodView):
    """ Handles a REST API call  """

    busy = False

    @classmethod
    async def get(cls, _):
        sanic = Sanic.get_app()
        Personas.purge(sanic.config.personaExpiration)

        if HeartbeatHandler.busy:
            return json({}, status=202, content_type='application/json')
        else:
            return json({}, status=200, content_type='application/json')
