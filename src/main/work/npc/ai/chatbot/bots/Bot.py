from typing import List

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, ConversationalPipeline, Conversation


class Bot:
    nlp = None

    @classmethod
    def useModel(cls, modelName="facebook/blenderbot-1B-distill"):
        tokenizer = AutoTokenizer.from_pretrained(modelName)
        model = AutoModelForSeq2SeqLM.from_pretrained(modelName)
        cls.nlp = ConversationalPipeline(model=model, tokenizer=tokenizer)

    def __init__(self, name: str, persona: List[str] = None, modelName=None):
        if not self.nlp:
            self.useModel(modelName) if modelName else self.useModel()

        self.name = name
        self.persona = persona
        self.conversation = None
        self.reset()

    def reset(self):
        self.conversation = Conversation()
        facts = f"My name is {self.name}.  "

        if self.persona:
            facts = facts + ".  ".join(self.persona)

        self.conversation.add_user_input('Hello')
        self.conversation.append_response(facts)
        self.conversation.mark_processed()

    def respondTo(self, utterance: str, show=False):
        if show:
            print(f">> {utterance}")

        self.conversation.add_user_input(utterance)
        result = self.nlp([self.conversation], do_sample=False, max_length=1000)
        *_, last = result.iter_texts()

        self.conversation.mark_processed()
        return last[1]
