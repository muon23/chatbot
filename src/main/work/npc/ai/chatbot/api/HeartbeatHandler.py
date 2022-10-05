from sanic import json
from sanic.views import HTTPMethodView


class HeartbeatHandler(HTTPMethodView):
    """ Handles a REST API call  """

    busy = False

    @classmethod
    async def get(cls, _):
        """ Responds to GET to the /heartbeat endpoint.

        :return: Response(200) if healthy, Response(202) if busy
        """
        if HeartbeatHandler.busy:
            return json({}, status=202, content_type='application/json')
        else:
            return json({}, status=200, content_type='application/json')
