import logging
import os

from sanic.config import Config

from work.npc.ai.chatbot.api.Version import Version
from work.npc.ai.utilities import Utilities
from work.npc.ai.utilities.TimeFormatter import TimeFormatter


class ChatBotServerConfig(Config):

    VERSION = Version.version

    def __init__(self, *args, **kwargs):
        debugConfig = kwargs.pop("providedConfig", None)
        debugArgs = kwargs.pop("providedArgs", None)

        super().__init__(*args, **kwargs)

        self.config = Utilities.getConfig(providedConfig=debugConfig, providedArgs=debugArgs)

        logging.info('Running from directory: %s', os.getcwd())

        chatBotConfig = self.config.get("chatbot", dict())

        self.basePath = chatBotConfig.get("basePath", "")
        self.personaExpiration = TimeFormatter.getDuration(chatBotConfig.get("personaExpiration", "1d"))
        self.botModel = chatBotConfig.get("botModel", "facebook/blenderbot-1B-distill")

        self.serverPort = int(chatBotConfig.get('serverPort', 8080))
        logging.info("Listening to port: %s", self.serverPort)
