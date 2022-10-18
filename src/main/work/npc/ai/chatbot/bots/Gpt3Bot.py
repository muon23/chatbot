import logging
import os
import re
import traceback
from typing import Iterator, Tuple, List

from work.npc.ai.chatbot.bots.Bot import Bot
import openai

from work.npc.ai.utilities.Languages import Languages


class Gpt3Conversation:
    def __changeSubject(self, fact, name):
        fact = fact.replace("I ", f"{name} ")
        fact = fact.replace(" am ", " is ")
        fact = fact.replace("My ", f"{name}'s ")
        return fact

    def __init__(self, name: str, persona: List[str], utteranceLimit: int):
        self.name = name
        self.persona = "  ".join([self.__changeSubject(fact, name) + "." for fact in persona])
        self.conversation: List[Tuple[bool, str]] = []
        self.utteranceLimit = utteranceLimit

    def add_user_input(self, utterance: str):
        self.conversation.append((True, utterance))

    def add_response(self, utterance: str):
        self.conversation.append((False, utterance))

    def getPrompt(self):
        return "\n".join(
            [self.persona, "========"] +

            [f"{'YOU' if user else f'{self.name}'}: {utt}"
             for user, utt in self.conversation[-2 * self.utteranceLimit - 1:]
             ]
        ) + f"\n{self.name}: "


class Gpt3Bot(Bot):
    completion = None

    @classmethod
    def of(cls, persona: List[str] = None, name: str = "Bot", modelName: str = None, utteranceLimit: int = 10) -> Bot:
        return Gpt3Bot(persona, name, utteranceLimit) if modelName.lower() == "gpt3" else None

    def __init__(self, persona: List[str] = None, name: str = "Bot", utteranceLimit: int = 10):
        if not self.completion:
            accessKey = os.environ.get("OPENAI_KEY")
            if not accessKey:
                raise RuntimeError("Environment OPENAI_KEY not defined")

            try:
                openai.api_key = accessKey
                self.completion = openai.Completion()
            except Exception as e:
                raise RuntimeError(f"Cannot access GPT-3. {str(e)}")

        self.conversation = Gpt3Conversation(name, persona, utteranceLimit)

    def __isGoodResponse(self, response: str) -> str:
        try:
            logging.info(f"Open AI response: {response}")

            # Take only the response up to the next speaker
            response = re.split(f"YOU: |{self.conversation.name}: ", response)[0]

            response = response.replace("\xa0", " ")    # Extended ASCII for nonbreakable space
            response = response.replace("\\n", " ")     # Sometimes, GPT-3 will put in "\n"

            if Languages.hanziSentences(response):
                # For filtering Chinese
                response = response.split("\n")[0]      # Only get the first line
            else:
                # For other alphabetical text
                response = response.split("\n\n")[0]        # Discard anything after double new lines
                response = response.replace("\n", " ")      # Concatenate multiple lines into one
                response = re.findall("[-A-Za-z0-9,.:;?! \"\']+", response)[0]   # Pick one that looks like a chat

            response = response.strip()
            logging.info(f"Extracted response: {response}")

        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(response)
            response = None

        return response

    def respondTo(self, utterance: str, **kwargs):
        self.conversation.add_user_input(utterance)
        prompt = self.conversation.getPrompt()
        # print(prompt)

        response = None
        while not response:
            response = self.completion.create(
                prompt=prompt,
                engine="davinci",
                stop=None,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                best_of=1,
                max_tokens=100
            )
            response = response.choices[0].text.strip()
            response = self.__isGoodResponse(response)

        self.conversation.add_response(response)
        return response

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        return self.conversation.conversation

    def getPersona(self) -> str:
        return self.conversation.persona

    def getModelName(self) -> str:
        return "GPT-3 Davinci"

    def reset(self):
        self.conversation.conversation = []
