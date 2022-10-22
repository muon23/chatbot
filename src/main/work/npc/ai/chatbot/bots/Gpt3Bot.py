import logging
import os
import re
import traceback
from typing import Iterator, Tuple, List, Optional

from work.npc.ai.chatbot.bots.Bot import Bot
import openai

from work.npc.ai.utilities.Languages import Languages


class Gpt3Conversation:
    @classmethod
    def __changeSubject(cls, fact, name):
        fact = fact.replace("我", name)
        fact = fact.replace("你", "我")

        words = fact.split()
        changed = []
        for word in words:
            changed.append(
                name if word == "I" else
                "is" if word == "am" else
                f"{name}'s" if word == "my" or word == "My" else
                "me" if word == "you" else
                word
            )

        return " ".join(changed)

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

            [f"{'Me' if user else f'{self.name}'}: {utt}"
             for user, utt in self.conversation[-2 * self.utteranceLimit - 1:]
             ]
        ) + f"\n{self.name}: "


class Gpt3Bot(Bot):
    completion = None

    __DEFAULT_UTTERANCE_LIMIT = 20

    @classmethod
    def of(
            cls,
            persona: List[str] = None,
            name: str = "Bot",
            modelName: str = None,
            utteranceLimit: int = __DEFAULT_UTTERANCE_LIMIT
    ) -> Bot:
        return Gpt3Bot(persona, name, utteranceLimit) if modelName.lower() == "gpt3" else None

    def __init__(self, persona: List[str] = None, name: str = "Bot", utteranceLimit: int = __DEFAULT_UTTERANCE_LIMIT):
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

    def __isGoodResponse(self, response: str) -> Optional[str]:
        try:
            logging.info(f"Open AI response: {response}")

            # Take only the response up to the next speaker
            response = re.split(f"Me: |{self.conversation.name}: ", response)[0]

            response = response.replace("\xa0", " ")    # Extended ASCII for nonbreakable space
            response = response.replace("\\n", " ")     # Sometimes, GPT-3 will put in "\n"

            if Languages.hanziSentences(response):
                # For filtering Chinese
                response = response.split("\n")[0]      # Only get the first line
            else:
                # For other alphabetical text
                response = response.split("\n\n")[0]        # Discard anything after double new lines
                if not re.findall("[A-Za-z0-9]", response):
                    return None                             # The response contains no alphanumerical letters
                response = response.replace("\n", " ")      # Concatenate multiple lines into one
                response = re.findall("[-A-Za-z0-9,.:;?! \"\']+", response)[0]   # Pick one that looks like a chat

            response = response.strip()
            logging.info(f"Extracted response: {response}")
            return response

        except Exception as e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            logging.error(response)
            return None

    def respondTo(self, utterance: str, **kwargs)  -> Optional[str]:
        self.conversation.add_user_input(utterance)
        prompt = self.conversation.getPrompt()
        # print(prompt)

        response = None
        while not response:
            try:
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

            except openai.error.APIConnectionError as e:
                logging.warning(f"GPT-3 access issue: {str(e)}")
                return None

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
