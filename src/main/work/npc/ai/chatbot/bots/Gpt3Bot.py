import logging
import os
import re
from typing import Iterator, Tuple, List, Optional, Set

from work.npc.ai.chatbot.bots.Bot import Bot
from work.npc.ai.chatbot.bots.Gpt3BotConversation import Gpt3BotConversation
from work.npc.ai.utilities.Gpt3Portal import Gpt3Portal
from work.npc.ai.utilities.Languages import Languages


class Gpt3Bot(Bot):
    __portal: Gpt3Portal = None

    __DEFAULT_UTTERANCE_LIMIT = 30
    __DEFAULT_TEMPERATURE = 0.9

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
        super().__init__(name)

        if not self.__portal:
            accessKey = os.environ.get("OPENAI_KEY")
            if not accessKey:
                raise RuntimeError("Environment OPENAI_KEY not defined")

            self.__portal = Gpt3Portal.of(accessKey)

        self.conversation = Gpt3BotConversation(self.name, persona, utteranceLimit)
        self.tokenLimit = 200

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
            utterance = m.group(3)

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
                utterance = re.findall("[^-.,)=!?*_][-A-Za-z0-9,.:;?! \"\'()]+", utterance)[0]

            utterance = utterance.strip()
            logging.info(f"Extracted response: {utterance}")

            return speaker, utterance if not self.conversation.isSimilarToLast(speaker, utterance) else None

        except Exception as e:
            logging.info(f"Bad utterance: {str(e)}")
            return None, None

    def processResponse(self, response: str, nextSpeaker: str = None) -> Tuple[Set[str], List[str]]:
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
                self.conversation.addUtterance(utterance, speaker=speaker)
                replies.append(self.conversation.getLine(speaker, utterance))
                spoken.add(speaker)

        self.conversation.promptMoreUtterances()
        return spoken, replies

    async def respondTo(self, utterance: str, **kwargs) -> Optional[str]:
        debug = kwargs.get("debug", False)

        speakers = kwargs.get("next", set())
        speakers.update(re.findall(r"@(\w+)", utterance))
        utterance = utterance.replace("@", "")

        if not speakers:
            speakers = {self.conversation.name}

        self.conversation.addUtterance(utterance, speaker=self.conversation.me)

        replies = []
        while speakers:
            nextSpeaker = speakers.pop()
            if debug:
                print(f"Speakers needed: {speakers}")

            prompt = self.conversation.getPrompt(nextSpeaker)
            print(prompt) if debug else None

            response = None
            tokenLimit = self.tokenLimit
            while not response:
                try:
                    response = await self.__portal.complete(
                        prompt=prompt,
                        retries=5,
                        stop=f"{self.conversation.me}: ",
                        temperature=self.__DEFAULT_TEMPERATURE,
                        max_tokens=tokenLimit
                    )

                    response = response[0]
                    logging.info(f">>>> OpenAI response:\n{response}")

                    spoken, lines = self.processResponse(response, nextSpeaker)
                    if lines:
                        replies += lines
                        speakers.difference_update(spoken)
                    else:
                        response = None
                        continue

                except Gpt3Portal.TooManyTokensError as e:
                    if tokenLimit <= 900:
                        tokenLimit += 100
                        logging.info(f"GPT-3 token limit exceeded.  Extending to {tokenLimit}.\n{str(e)}")
                    elif self.conversation.fewerUtterances():
                        prompt = self.conversation.getPrompt()
                        print(prompt) if debug else None
                    else:
                        errorMsg = f"Minimum utterances {self.conversation.currentUtteranceLimit} "
                        "and maximum tokens {tokenLimit}, Use shorter utterances."
                        logging.warning(errorMsg)
                        raise RuntimeError(errorMsg)

        return "\n".join(replies)

    def getConversation(self) -> Iterator[str]:
        for c in self.conversation.conversation:
            speaker = "You" if c.speaker == self.conversation.me else c.speaker
            hidden = ' (hidden)' if c.hidden else ''
            yield self.conversation.getLine(speaker, c.utterance + hidden)

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

    def modifyConversation(self, instruction=None, **kwargs):
        if instruction is None:
            instruction = dict()

        if instruction.get("reset", False):
            self.conversation.reset()

        restore = instruction.get("restore", [])
        if restore:
            self.conversation.restore(restore)

        if instruction.get("remove_ai", False):
            self.conversation.removeAi()

        if instruction.get("hide_ai", False):
            self.conversation.hideAi()

        hide = instruction.get("hide", [])
        if hide:
            self.conversation.hide(set(self.__makeIndices(hide, self.conversation.length())))

        show = instruction.get("show", [])
        if show:
            self.conversation.show(set(self.__makeIndices(show, self.conversation.length())))

        if instruction.get("redo", None):
            self.conversation.redo()

        replace = instruction.get("replace", [])
        if isinstance(replace, str):
            replace = [replace]

        for r in replace:
            if isinstance(r, str):
                idx, replacement = self.__parseReplacement(r)
                self.conversation.replace(replacement, idx)

        erase = instruction.get("erase", [])
        if erase:
            self.conversation.erase(set(self.__makeIndices(erase, self.conversation.length())))

        script = instruction.get("script", None)
        if isinstance(script, str):
            script = [script]

        if isinstance(script, list):
            nextSpeaker = self.conversation.nextSpeaker()

            for line in script:

                if not isinstance(line, str):
                    continue

                # Get the speaker
                m = re.match(r"\s*((\S+):)?\s*(.+)\s*$", line)
                if not m:
                    continue
                speaker = m.group(2) if m.group(2) else self.conversation.NARRATION
                utterance = m.group(3)

                if speaker == self.conversation.NARRATION and not re.match(r"\(.*\)", utterance):
                    speaker = nextSpeaker

                self.conversation.addUtterance(
                    utterance=utterance,
                    speaker=speaker
                )
                nextSpeaker = speaker
