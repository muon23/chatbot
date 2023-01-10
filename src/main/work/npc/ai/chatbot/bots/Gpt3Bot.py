import json
import logging
import os
import random
import re
from typing import Iterator, Tuple, List, Optional, Set

from work.npc.ai.chatbot.bots.Bot import Bot
from work.npc.ai.chatbot.bots.Gpt3BotConversation import Gpt3BotConversation
from work.npc.ai.utilities.Gpt3Portal import Gpt3Portal
from work.npc.ai.utilities.Languages import Languages


class Gpt3Bot(Bot):
    __portal: Gpt3Portal = None

    __MODEL_NAME = "GPT-3 Davinci"
    __DEFAULT_TEMPERATURE = 0.9
    __DEFAULT_OUTPUT_TOKENS = 200

    @classmethod
    def of(cls, persona: List[str] = None, modelName: str = None, **kwargs) -> Bot:
        return Gpt3Bot(persona, **kwargs) if modelName.lower() in ["gpt3", cls.__MODEL_NAME.lower()] else None

    def __init__(self, persona: List[str] = None, **kwargs):
        super().__init__(**kwargs)

        if not self.__portal:
            accessKey = os.environ.get("OPENAI_KEY")
            if not accessKey:
                raise RuntimeError("Environment OPENAI_KEY not defined")

            self.__portal = Gpt3Portal.of(accessKey)

        self.persona = persona
        kwargs["name"] = self.name
        self.conversation = Gpt3BotConversation(self.persona, **kwargs)
        self.maxOutputTokens = self.__DEFAULT_OUTPUT_TOKENS
        self.next2talk = set()

    def parseUtterance(self, utterance: str) -> Tuple[Optional[str], Optional[str]]:
        if not utterance:
            return None, None

        try:
            # Take only the utterance up to the next speaker
            utterance = utterance.replace("\xa0", " ")  # Extended ASCII for nonbreakable space
            utterance = utterance.replace("\\n", " ")  # Sometimes, GPT-3 will put in "\n"

            # Get the speaker
            m = re.match(r"\s*((\S+):)?\s*(.+)\s*$", utterance)
            speaker = m.group(2) if m.group(2) else self.conversation.NARRATION
            utterance = m.group(3).strip()

            if speaker == self.conversation.me:
                # Me the user shall not be part of AI's response.
                return None, None

            if any([Languages.isIdeography(c) for c in utterance]):
                # For filtering Chinese
                pass

            else:
                # For other alphabetical text
                if not re.findall("[A-Za-z0-9]", utterance):
                    return None, None  # The utterance contains no alphanumerical letters

                # Look the first section that looks like a chat
                utterance = re.findall(r"[^-.,)=!?*_][-A-Za-z0-9,.:;?! \"'()&%$#]+", utterance)[0]

            logging.info(f"Extracted response: {utterance}")

            return speaker, utterance if not self.conversation.isSimilarToLast(speaker, utterance) else None

        except Exception as e:
            logging.info(f"Bad utterance: {str(e)}")
            return None, None

    async def processResponse(self, response: str, nextSpeaker: str = None) -> Tuple[Set[str], List[str]]:
        utterances = response.split("\n")
        replies = []
        spoken = set()
        for i, utterance in enumerate(utterances):
            speaker, utterance = self.parseUtterance(utterance)
            if not speaker:
                continue  # Parse error

            if i == 0 and speaker == self.conversation.NARRATION:
                speaker = nextSpeaker if nextSpeaker else self.conversation.name

            if utterance:
                await self.conversation.addUtterance(utterance, speaker=speaker)
                replies.append(self.conversation.getLine(speaker, utterance))
                spoken.add(speaker)

        return spoken, replies

    async def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        debug = kwargs.get("debug", False)
        temperature = kwargs.get("temperature", self.__DEFAULT_TEMPERATURE)

        speakers = kwargs.get("next", [])
        if not isinstance(speakers, list):
            speakers = [speakers]
        speakers = set(speakers)
        speakers.update(self.next2talk)
        self.next2talk = []
        speakers.update(re.findall(r"@(\w+)", utterance))
        utterance = utterance.replace("@", "")

        if not speakers:
            speakers = {self.conversation.name}

        await self.conversation.addUtterance(utterance, speaker=self.conversation.me)

        after = kwargs.get("after", [])
        if after:
            await self.conversation.script(after)

        replies = []
        while speakers:
            nextSpeaker = speakers.pop()
            if debug:
                print(f"Speakers needed: {speakers}")

            prompt = self.conversation.getPrompt(nextSpeaker)
            print(prompt) if debug else None

            response = None
            tokenLimit = self.maxOutputTokens
            while not response:
                try:
                    response = await self.__portal.complete(
                        prompt=prompt,
                        retries=5,
                        stop=f"{self.conversation.me}: ",
                        temperature=temperature,
                        max_tokens=tokenLimit
                    )

                    response = response[0]
                    logging.info(f">>>> OpenAI response:\n{response}")

                    spoken, lines = await self.processResponse(response, nextSpeaker)
                    if lines:
                        replies += lines
                        speakers.difference_update(spoken)
                    else:
                        response = None
                        continue

                except Gpt3Portal.TooManyTokensError as e:
                    message = f"Story too long.  {str(e)}"
                    logging.warning(message)
                    raise RuntimeError(message)

        save = kwargs.get("save", None)
        if save:
            self.save(save)

        return "\n".join(replies)

    def save(self, file: str):
        persona = {
            "persona": self.persona,
            "name": self.name,
            "model": self.__MODEL_NAME
        }
        if self.conversation.me not in ["我", "I"]:
            persona["you"] = self.conversation.me

        script = list(self.getConversation())

        toSave = {"persona": persona, "script": script}
        file = os.path.expanduser(file)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            json.dump(toSave, f)

    async def load(self, script: List[str]):
        await self.conversation.script(script)

    def getConversation(self) -> Iterator[str]:
        for c in self.conversation.conversation:
            speaker = "You" if c.speaker == "I" else "你" if c.speaker == "我" else c.speaker
            yield self.conversation.getLine(speaker, c.utterance)

    def getPersona(self):
        return self.persona

    def getModelName(self) -> str:
        return self.__MODEL_NAME

    @staticmethod
    def __makeIndices(specs, last: int) -> Iterator[int]:
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
                        end = last - 1

                    yield from range(begin, end + 1)

    async def modifyConversation(self, instruction=None, **kwargs):
        if instruction is None:
            instruction = dict()

        if instruction.get("reset", False):
            self.conversation.reset()

        restore = instruction.get("restore", [])
        if restore:
            await self.conversation.restore(restore)

        if instruction.get("redo", None):
            self.conversation.redo()

        replace = instruction.get("replace", None)
        if replace:
            await self.conversation.replace(replace)

        erase = instruction.get("erase", [])
        if erase:
            await self.conversation.erase(set(self.__makeIndices(erase, self.conversation.length())))

        script = instruction.get("script", None)
        if script:
            await self.conversation.script(script)

        insert = instruction.get("insert", None)
        if insert:
            await self.conversation.insert(insert)

        next2talk = instruction.get("next", [])
        self.next2talk = set(next2talk) if isinstance(next2talk, list) else {next2talk}

        randomTalk = instruction.get("random", [])
        if randomTalk:
            randomTalk = set(randomTalk) if isinstance(randomTalk, list) else {randomTalk}
            chance = 1/len(randomTalk)
            for r in randomTalk:
                if random.random() < chance:
                    self.next2talk.add(r)

        replaceMe = instruction.get("me", None)
        if replaceMe:
            self.conversation.replaceMe = replaceMe
