import difflib
import logging
import os
import re
import traceback
from typing import Iterator, Tuple, List, Optional, Set

import openai

from work.npc.ai.chatbot.bots.Bot import Bot
from work.npc.ai.utilities.Languages import Languages


class Gpt3Utterance:
    def __init__(self, isUser: bool, utterance: str):
        self.isUser = isUser
        self.utterance = utterance
        self.hidden = False


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
        self.conversation: List[Gpt3Utterance] = []
        self.utteranceLimit = utteranceLimit

        self.me = "我" if any([Languages.isIdeography(c) for c in self.name]) else "Me"

        logging.info(f"Persona: {self.persona}")
        logging.info(f"Utterance limit: {self.utteranceLimit}")

    def addUtterance(self, utterance: str, fromUser: Optional[bool] = None):
        if fromUser is None:
            fromUser = self.isUserSpeaksNext()

        self.conversation.append(Gpt3Utterance(fromUser, utterance))

    def reset(self):
        self.conversation = []

    def removeAi(self):
        self.conversation = [c for i, c in enumerate(self.conversation) if c.isUser]

    def erase(self, indices: Set[int]):
        if not indices:
            return

        indices = sorted(indices)
        remain = []
        begin = 0
        for idx in indices:
            if idx > begin:
                remain += self.conversation[begin:idx]
            elif idx >= self.length() - 1:
                break

            begin = idx + 1

        self.conversation = remain + self.conversation[indices[-1]+1:]

    def redo(self):
        # Clear anything after and include the last utterance from the user
        try:
            while not self.conversation[-1].isUser:
                self.conversation.pop()
            self.conversation.pop()
        except IndexError:
            pass

    def hide(self, hidden: Set[int]):
        for i in hidden:
            self.conversation[i].hidden = True

    def show(self, show: Set[int]):
        for i in show:
            self.conversation[i].hidden = False

    def hideAi(self):
        for c in self.conversation:
            if not c.isUser:
                c.hidden = True

    def replace(self, utterance: str, idx: int = None):
        if idx is None:
            if len(self.conversation) == 0:
                self.addUtterance(utterance)
                return
            else:
                idx = -1

        self.conversation[idx].utterance = utterance

    def __withSpeaker(self, utterance: Gpt3Utterance) -> str:
        who = self.me if utterance.isUser else self.name
        return f"{who}: {utterance.utterance}"

    def getPrompt(self):
        utterances = []
        for u in reversed(self.conversation):
            if not u.hidden:
                utterances.append(self.__withSpeaker(u))
                if len(utterances) > self.utteranceLimit:
                    break
        utterances.reverse()

        return "\n".join([self.persona, "========"] + utterances) + f"\n{self.name}: "

    def isSimilarToLast(self, response: str, threshold=0.6) -> bool:
        if len(self.conversation) < 2:
            return False

        previousResponse = self.conversation[-2].utterance
        similarity = difflib.SequenceMatcher(None, response, previousResponse).ratio()
        if similarity > threshold:
            logging.info(f"Too similar to previous.  Similarity: {similarity}  Threshold: {threshold}")
            logging.info(f"    '{response}' vs '{previousResponse}'")
            return True

        return False

    def isUserSpeaksNext(self):
        return not self.conversation[-1].isUser if len(self.conversation) > 0 else True

    def length(self):
        return len(self.conversation)

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
            response = re.split(f"{self.conversation.me}: ", response)[0]

            response = response.replace(f"\n{self.conversation.name}: ", " ")  # The speaker remain the same
            response = response.replace("\xa0", " ")  # Extended ASCII for nonbreakable space
            response = response.replace("\\n", " ")  # Sometimes, GPT-3 will put in "\n"

            if any([Languages.isIdeography(c) for c in response]):
                # For filtering Chinese
                response = response.split("\n")[0]  # Only get the first line
            else:
                # For other alphabetical text
                response = response.split("\n\n")[0]  # Discard anything after double new lines
                if not re.findall("[A-Za-z0-9]", response):
                    return None  # The response contains no alphanumerical letters
                response = response.replace("\n", " ")  # Concatenate multiple lines into one
                response = re.findall("[-A-Za-z0-9,.:;?! \"\'()]+", response)[0]  # Pick one that looks like a chat

            response = response.strip()
            logging.info(f"Extracted response: {response}")

            return response if not self.conversation.isSimilarToLast(response) else None

        except Exception as e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            logging.error(response)
            return None

    def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        debug = kwargs.get("debug", False)

        self.conversation.addUtterance(utterance, fromUser=True)
        prompt = self.conversation.getPrompt()
        print(prompt) if debug else None

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

            except openai.error.APIConnectionError as e:
                logging.warning(f"GPT-3 access issue: {str(e)}")
                return None

        self.conversation.addUtterance(response, fromUser=False)
        return response

    def getConversation(self) -> Iterator[Tuple[bool, str]]:
        return ((c.isUser, f"{c.utterance}{' (hidden)' if c.hidden else ''}") for c in self.conversation.conversation)

    def getPersona(self) -> str:
        return self.conversation.persona

    def getModelName(self) -> str:
        return "GPT-3 Davinci"

    @staticmethod
    def __parseReplacement(replacement: str):
        m = re.match(r"\s*((\d+)\s*:\s*)?(.+)", replacement)
        idx, replacement = m.group(2), m.group(3)
        idx = int(idx) if idx else None
        return idx, replacement

    @staticmethod
    def __makeIndices(specs, last:int) -> Iterator[int]:
        if isinstance(specs, int):
            yield specs

        if isinstance(specs, str):
            specs = [specs]

        if isinstance(specs, list):
            for s in specs:
                if isinstance(s, int):
                    yield s

                elif isinstance(s, str):
                    m = re.match(r"\s*(\d+)?\s*([-:]\s*(\d+)?)?", s)
                    if m is None:
                        continue

                    begin = 0 if m.group(1) is None else int(m.group(1))

                    if m.group(2) is None and m.group(1) is not None:
                        yield begin
                        continue

                    end = last if m.group(3) is None else int(m.group(3))
                    if end >= last:
                        end = last-1

                    yield from range(begin, end+1)

    def modifyConversation(self, instruction=None, **kwargs):
        if instruction is None:
            instruction = dict()

        if instruction.get("reset", False):
            self.conversation.reset()

        if instruction.get("remove_ai", False):
            self.conversation.removeAi()

        if instruction.get("hide_ai", False):
            self.conversation.hideAi()

        hide = instruction.get("hide", [])
        self.conversation.hide(set(self.__makeIndices(hide, self.conversation.length())))

        show = instruction.get("show", [])
        self.conversation.show(set(self.__makeIndices(show, self.conversation.length())))

        if instruction.get("redo", None):
            self.conversation.redo()

        replace = instruction.get("replace", [])
        if isinstance(replace, str):
            replace = [replace]

        if isinstance(replace, list):
            for r in replace:
                if isinstance(r, str):
                    idx, replacement = self.__parseReplacement(r)
                    self.conversation.replace(replacement, idx)

        erase = instruction.get("erase", [])
        self.conversation.erase(set(self.__makeIndices(erase, self.conversation.length())))

        script = instruction.get("script", [])
        if isinstance(script, list):
            nextSpeaker = self.conversation.isUserSpeaksNext()
            for s in script:
                if isinstance(s, str):
                    s = [s]

                if not isinstance(s, list):
                    continue

                if isinstance(s[0], bool):
                    self.conversation.addUtterance(utterance="  ".join(s[1:]), fromUser=s[0])
                elif isinstance(s[0], int):
                    self.conversation.addUtterance(utterance="  ".join(s[1:]), fromUser=s[0] == 1)
                else:
                    self.conversation.addUtterance("  ".join(s))

