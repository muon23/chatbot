from typing import List, Iterator, Tuple, Optional

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, ConversationalPipeline, Conversation

from work.npc.ai.chatbot.bots.Bot import Bot


class TransformerBot(Bot):
    models: dict = dict()

    __DEFAULT_MODEL = "facebook/blenderbot-1B-distill"

    @classmethod
    def of(cls, persona: List[str] = None, modelName=__DEFAULT_MODEL) -> Bot:
        return TransformerBot(persona, modelName) if modelName in [
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill",
            "facebook/blenderbot-3B",
            cls.__DEFAULT_MODEL
        ] else None

    def __init__(self, persona: List[str] = None, modelName=__DEFAULT_MODEL):
        self.modelName = modelName
        if modelName not in self.models:
            tokenizer = AutoTokenizer.from_pretrained(modelName)
            model = AutoModelForSeq2SeqLM.from_pretrained(modelName)
            self.models[modelName] = ConversationalPipeline(model=model, tokenizer=tokenizer)

        self.persona = persona
        self.conversation = None
        self.reset()

    def reset(self, **kwargs):
        self.conversation = Conversation()
        facts = ".  ".join(self.persona) if self.persona else ""
        self.conversation.add_user_input('Hello')
        self.conversation.append_response(facts)
        self.conversation.mark_processed()

    def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        self.conversation.add_user_input(utterance)
        model = self.models[self.modelName]
        result = model([self.conversation], do_sample=False, max_length=1000)
        *_, last = result.iter_texts()

        self.conversation.mark_processed()
        return last[1]

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        conv = self.conversation.iter_texts()
        next(conv)  # The first two are fake conversation to inject persona
        next(conv)
        return conv

    def getPersona(self) -> str:
        conv = self.conversation.iter_texts()
        next(conv)  # The first one is a fake user prompt "Hello"
        return next(conv)[1]

    def getModelName(self) -> str:
        return self.modelName
