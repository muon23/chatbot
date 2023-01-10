from typing import List, Iterator, Optional

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, ConversationalPipeline, Conversation

from work.npc.ai.chatbot.bots.Bot import Bot


class TransformerBot(Bot):
    models: dict = dict()

    __DEFAULT_MODEL = "facebook/blenderbot-1B-distill"

    @classmethod
    def of(cls, persona: List[str] = None, modelName=__DEFAULT_MODEL, **kwargs) -> Bot:
        return TransformerBot(persona, modelName, **kwargs) if modelName in [
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill",
            "facebook/blenderbot-3B",
            cls.__DEFAULT_MODEL
        ] else None

    def __init__(self, persona: List[str] = None, modelName=__DEFAULT_MODEL, **kwargs):
        super().__init__(**kwargs)

        self.modelName = modelName
        if modelName not in self.models:
            tokenizer = AutoTokenizer.from_pretrained(modelName)
            model = AutoModelForSeq2SeqLM.from_pretrained(modelName)
            self.models[modelName] = ConversationalPipeline(model=model, tokenizer=tokenizer)

        self.persona = persona
        self.conversation = None
        self.modifyConversationSync()

    def modifyConversationSync(self, instruction=None, **kwargs):
        if not self.conversation or (instruction and "reset" in instruction):
            self.conversation = Conversation()
            facts = ".  ".join(self.persona) if self.persona else ""
            self.conversation.add_user_input('Hello')
            self.conversation.append_response(facts)
            self.conversation.mark_processed()

    async def modifyConversation(self, instruction=None, **kwargs):
        self.modifyConversationSync(instruction)

    async def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        self.conversation.add_user_input(utterance)
        model = self.models[self.modelName]
        result = model([self.conversation], do_sample=False, max_length=1000)
        *_, last = result.iter_texts()

        self.conversation.mark_processed()
        return last[1]

    def getConversation(self) -> Iterator[str]:
        conv = self.conversation.iter_texts()
        next(conv)  # The first two are fake conversation to inject persona
        next(conv)

        for utterance in conv:
            speaker = "You" if utterance[0] else self.name
            yield f"{speaker}: {utterance[1]}"

    def getPersona(self) -> str:
        conv = self.conversation.iter_texts()
        next(conv)  # The first one is a fake user prompt "Hello"
        return next(conv)[1]

    def getModelName(self) -> str:
        return self.modelName

    async def load(self, script: List[str]):
        raise NotImplemented(f"Loading from file is not supported for model '{self.getModelName()}'")
