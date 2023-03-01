import sys

transformer_models = ["facebook/blenderbot-400M-distill",
                      "facebook/blenderbot-1B-distill",
                      "facebook/blenderbot-3B"]

parlai_models = ["zoo:blender/blender_400M/model",
                 "zoo:blender/blender_3B/model",
                 "zoo:bb3/bb3_3B/model"]

modelName = sys.argv[1]
print(f"Downloading model: {modelName}")
if modelName in transformer_models:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer = AutoTokenizer.from_pretrained(modelName)
    model = AutoModelForSeq2SeqLM.from_pretrained(modelName)

if modelName in parlai_models:
    from parlai.core.agents import create_agent_from_model_file
    agent = create_agent_from_model_file(modelName)

if modelName == "gpt2tokenizer":
    from transformers import GPT2TokenizerFast
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    print(tokenizer("use this to download models")["input_ids"])
