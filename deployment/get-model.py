import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/main')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../commons/src/main')))

from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


model = sys.argv[1]
print(f"Downloading model: {model}")
bot = TransformerBot.of(modelName=model) or ParlaiBot.of(modelName=model)
bot.respondTo("Hi")

