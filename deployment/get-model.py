# import os
import sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/main')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../commons/src/main')))
#
# # from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
# from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot
#
#
# model = sys.argv[1]
# print(f"Downloading model: {model}")
# bot = TransformerBot.of(modelName=model) #or ParlaiBot.of(modelName=model)
# bot.respondTo("Hi")


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GPT2TokenizerFast
from parlai.core.agents import create_agent_from_model_file

transformer_models = ["facebook/blenderbot-400M-distill",
                      "facebook/blenderbot-1B-distill",
                      "facebook/blenderbot-3B"]

parlai_models = ["zoo:blender/blender_400M/model",
                 "zoo:blender/blender_3B/model",
                 "zoo:bb3/bb3_3B/model"]

modelName = sys.argv[1]
print(f"Downloading model: {modelName}")
if modelName in transformer_models:
    tokenizer = AutoTokenizer.from_pretrained(modelName)
    model = AutoModelForSeq2SeqLM.from_pretrained(modelName)

if modelName in parlai_models:
    agent = create_agent_from_model_file(modelName)

if modelName == "gpt2tokenizer":
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    print(tokenizer("use this to download models")["input_ids"])
