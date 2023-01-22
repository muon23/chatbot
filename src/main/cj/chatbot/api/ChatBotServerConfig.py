import logging
import os

from sanic.config import Config

from cj.chatbot.api.Version import Version
from cj.utilities import Utilities
from cj.utilities.TimeFormatter import TimeFormatter


class ChatBotServerConfig(Config):

    VERSION = Version.version

    def __init__(self, *args, **kwargs):
        debugConfig = kwargs.pop("providedConfig", None)
        debugArgs = kwargs.pop("providedArgs", None)

        super().__init__(*args, **kwargs)

        self.config = Utilities.getConfig(providedConfig=debugConfig, providedArgs=debugArgs)

        logging.info('Running from directory: %s', os.getcwd())

        self.basePath = self.config.get("basePath", "")
        self.personaExpiration = TimeFormatter.getDuration(self.config.get("personaExpiration", "1d"))
        self.botModel = self.config.get("botModel", "facebook/blenderbot-1B-distill")
        self.gpt3Limit = self.config.get("gpt3Limit", 50)
        self.debug = self.config.get("debug", None)

        self.serverPort = int(self.config.get('serverPort', 8080))
        logging.info("Listening to port: %s", self.serverPort)
