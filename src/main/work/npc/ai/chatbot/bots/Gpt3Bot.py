import difflib
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
                name if word == "I" or word == "me" else
                "is" if word == "am" else
                f"{name}'s" if word == "my" or word == "My" else
                "I" if word == "You" else
                "me" if word == "you" else
                "my" if word == "your" else
                "mine" if word == "yours" else
                "myself" if word == "yourself" else
                word
            )
        fact = " ".join(changed)

        fact = re.sub(r"I\s+are", "I am", fact)
        fact = re.sub(r"I\s+were", "I was", fact)

        return fact

    def __init__(self, name: str, persona: List[str], utteranceLimit: int):
        self.name = name
        self.persona = "  ".join([self.__changeSubject(fact, name) + "." for fact in persona]) if persona else []
        self.conversation: List[Tuple[bool, str, bool]] = []
        self.utteranceLimit = utteranceLimit

    def add_user_input(self, utterance: str):
        self.conversation.append((True, utterance, True))

    def add_response(self, utterance: str):
        self.conversation.append((False, utterance, True))

    def reset(self):
        self.conversation = []

    def resetAi(self):
        self.conversation = [c for i, c in enumerate(self.conversation) if c[0] is False]

    def erase(self, begin, end):
        if not begin:
            begin = 0
        if not end:
            end = len(self.conversation) - 1
        self.conversation = self.conversation[:begin-1] + self.conversation[end+1:]

    def resetLast(self):
        # Clear anything after and include the last utterance from the user
        try:
            while self.conversation[-1][0] is False:
                self.conversation.pop()
            self.conversation.pop()
        except IndexError:
            pass

    def hide(self, hidden: List[int]):
        for i, u in enumerate(self.conversation):
            if i in hidden:
                self.conversation[i] = u[0], u[1], False
            elif -i in hidden:
                self.conversation[i] = u[0], u[1], True

    def hideAi(self):
        for i, u in enumerate(self.conversation):
            self.conversation[i] = u[0], u[1], i % 2 == 0

    def replace(self, utterance: str, idx: int = None):
        numUtterance = len(self.conversation)
        if idx is None:
            idx = numUtterance - 1

        if idx < numUtterance:
            self.conversation[idx] = self.conversation[idx][0], utterance, self.conversation[idx][2]
        elif idx % 2 == 0 ^ self.conversation[0][0]:
            self.add_response(utterance=utterance)
        else:
            self.add_user_input(utterance=utterance)

    def getPrompt(self):
        return "\n".join(
            [self.persona, "========"] +

            [f"{'Me' if user else f'{self.name}'}: {utt}"
             for user, utt, show in self.conversation[-2 * self.utteranceLimit - 1:]
             if show
             ]
        ) + f"\n{self.name}: "


class Gpt3Bot(Bot):
    completion = None

    __DEFAULT_UTTERANCE_LIMIT = 30

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
            response = re.split(f"Me: ", response)[0]

            response = response.replace(f"\n{self.conversation.name}: ", " ")  # The speaker remain the same
            response = response.replace("\xa0", " ")    # Extended ASCII for nonbreakable space
            response = response.replace("\\n", " ")     # Sometimes, GPT-3 will put in "\n"

            if any([Languages.isIdeography(c) for c in response]):
                # For filtering Chinese
                response = response.split("\n")[0]      # Only get the first line
            else:
                # For other alphabetical text
                response = response.split("\n\n")[0]        # Discard anything after double new lines
                if not re.findall("[A-Za-z0-9]", response):
                    return None                             # The response contains no alphanumerical letters
                response = response.replace("\n", " ")      # Concatenate multiple lines into one
                response = re.findall("[-A-Za-z0-9,.:;?! \"\'()]+", response)[0]   # Pick one that looks like a chat

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
        tries = 0
        while not response and tries < 5:
            try:
                tries += 1
                response = self.completion.create(
                    prompt=prompt,
                    engine="davinci",
                    stop=None,
                    temperature=0.7,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                    best_of=1,
                    max_tokens=300
                )
                response = response.choices[0].text.strip()
                response = self.__isGoodResponse(response)

                if response:
                    previousResponse = self.conversation.conversation[-2] if len(self.conversation.conversation) >= 2 else None
                    similar = difflib.SequenceMatcher(None, response, f"{self.conversation.name}: {previousResponse}").ratio()
                    # print(f">>>> {similar} <<<<")
                    if similar > 0.6:
                        response = None

            except openai.error.APIConnectionError as e:
                logging.warning(f"GPT-3 access issue: {str(e)}")
                return None

        self.conversation.add_response(response)
        return response

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        return ((c[0], c[1]) for c in self.conversation.conversation)

    def getPersona(self) -> str:
        return self.conversation.persona

    def getModelName(self) -> str:
        return "GPT-3 Davinci"

    @staticmethod
    def __parseReplacement(replacement: str):
        p = re.compile(r"\s*((\d+)\s*:\s*)?(.+)")
        m = p.match(replacement)
        idx, replacement = m[2], m[3]
        idx = int(idx) if idx else None
        return idx, replacement

    def reset(self, how, **kwargs):
        if how is True:
            self.conversation.reset()
        elif isinstance(how, str):
            instruction = how.lower()

            if instruction == "reset ai":
                self.conversation.resetAi()
            elif instruction == "ai" or instruction == "hide ai":
                self.conversation.hideAi()
            elif instruction == "last":
                self.conversation.resetLast()
            elif instruction.startswith("erase"):
                m = re.match(r"erase\s*(\d+)?\s*:\s*(\d+)?", instruction)
                if m:
                    begin = int(m.group(1)) if m.group(1) else None
                    end = int(m.group(2)) if m.group(2) else None
                    self.conversation.erase(begin, end)
            else:  # Replace a previous utterance
                idx, replacement = self.__parseReplacement(instruction)
                self.conversation.replace(replacement, idx)
        elif isinstance(how, list):
            # Hiding some previous utterances from AI
            hide = [h for h in how if isinstance(h, int)]
            self.conversation.hide(hide)

            # Replaces previous utterances
            replace = [h for h in how if isinstance(h, str)]
            for r in replace:
                idx, replacement = self.__parseReplacement(r)
                self.conversation.replace(replacement, idx)

            # Add a script manually
            scripts = [h for h in how if isinstance(h, list)]
            currentSpeaker = None
            utterance = ""
            for s in scripts:
                if not isinstance(s, (bool, str)) and not isinstance(s, (bool, list)):
                    continue

                if currentSpeaker == s[0]:
                    utterance += s[1]
                else:
                    if currentSpeaker is not None:
                        if currentSpeaker:
                            self.conversation.add_user_input(utterance)
                        else:
                            self.conversation.add_response(utterance)

                    currentSpeaker = s[0]
                    if isinstance(s[1], str):
                        utterance = s[1]
                    elif isinstance(s[1], list):
                        utterance = "  ".join([ss for ss in s[1] if isinstance(ss, str)])

            if currentSpeaker:
                self.conversation.add_user_input(utterance)
            else:
                self.conversation.add_response(utterance)

