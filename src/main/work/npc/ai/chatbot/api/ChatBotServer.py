import logging

from sanic import Sanic
from sanic_cors import CORS

from work.npc.ai.chatbot.api.SummaryHandler import SummaryHandler
from work.npc.ai.chatbot.api.ChatHandler import ChatHandler
from work.npc.ai.chatbot.api.ChatBotServerConfig import ChatBotServerConfig
from work.npc.ai.chatbot.api.HeartbeatHandler import HeartbeatHandler
from work.npc.ai.chatbot.api.PersonaHandler import PersonaHandler
from work.npc.ai.chatbot.api.Version import Version


class ChatBotServer:
    """ A wrapper class that hosts the main program.  It reads configurations and starts a Flask server to handle
    REST API
    """

    @classmethod
    def main(cls, debugConfig=None, debugArgs=None):
        """ Starts a Flask API server

        :param debugConfig: Configuration given when called by the unit testing
        :param debugArgs: Configuration that passed in as command line arguments for unit testing
        """
        print(f'API server {Version.version} starting')
        config = ChatBotServerConfig(providedConfig=debugConfig, providedArgs=debugArgs)
        app = Sanic(cls.__name__, config=config)
        CORS(app)

        disables = config.config.get("disable", "").split(",")
        chatDisabled = "chat" in disables
        summaryDisabled = "summary" in disables

        app.add_route(HeartbeatHandler.as_view(), app.config.basePath + '/health')

        if chatDisabled:
            logging.info("Chat bot disabled")
        else:
            app.add_route(ChatHandler.as_view(), app.config.basePath + '/chat/<personaId>')
            app.add_route(PersonaHandler.as_view(), app.config.basePath + '/persona', methods=["POST"])
            app.add_route(
                PersonaHandler.as_view(), app.config.basePath + '/persona/<personaId>', methods=["DELETE", "GET"]
            )

        if summaryDisabled:
            logging.info("Summarizer disabled")
        else:
            app.add_route(SummaryHandler.as_view(), app.config.basePath + '/summary', methods=["POST"])

        # For local debug mode (serverPort=0), just run the API.
        # Otherwise, use waitress library to snippetStart a server that listen to the port.
        if app.config.serverPort == 0:
            app.run(debug=True)
        else:
            app.run(host='0.0.0.0', port=app.config.serverPort, single_process=True)


if __name__ == '__main__':
    ChatBotServer.main()
