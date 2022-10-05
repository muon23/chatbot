import logging
import os

from sanic.config import Config

from src.main.work.npc.ai.utilities import Utilities
from work.npc.ai.chatbot.api.Version import Version


class ChatbotServerConfig(Config):

    VERSION = Version.version
    SUPPORTED_APPS = {
        "text": {"chat", "note", "calendar", "reminder", "piece", "file"},
        "image": {"image"},
        "video": {"video"},
        "audio": {"audio"},
    }

    def __init__(self, *args, **kwargs):
        debugConfig = kwargs.pop("providedConfig", None)
        debugArgs = kwargs.pop("providedArgs", None)

        super().__init__(*args, **kwargs)

        self.config = Utilities.getConfig(providedConfig=debugConfig, providedArgs=debugArgs)

        logging.info('Running from directory: %s', os.getcwd())

        chatbotConfig = self.config.get("chatbot", dict())

        self.serverPort = chatbotConfig.get('serverPort', 8080)
        logging.info("Listening to port: %s", self.serverPort)
