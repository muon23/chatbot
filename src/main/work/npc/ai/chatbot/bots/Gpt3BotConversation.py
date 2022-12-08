import difflib
import logging
import re
from typing import Iterator, List, Optional, Set

from work.npc.ai.chatbot.summary.Gpt3Summarizer import Gpt3Summarizer
from work.npc.ai.utilities.Gpt3Portal import Gpt3Portal
from work.npc.ai.utilities.Languages import Languages


class Gpt3BotUtterance:
    def __init__(self, speaker: str, utterance: str):
        self.speaker = speaker
        self.utterance = utterance
        self.hidden = False
        self.tokens = Gpt3Portal.estimateTokens(Gpt3BotConversation.getLine(speaker, utterance))


class Gpt3BotSummary:
    __summarizer = None

    @classmethod
    async def of(cls, utterances: List[Gpt3BotUtterance], batchTokens: int = 3000) -> Iterator["Gpt3BotSummary"]:
        if not cls.__summarizer:
            cls.__summarizer = Gpt3Summarizer()

        tokens = 0
        lastIdx = 0
        text = ""
        for idx, utt in enumerate(utterances):
            if utt.hidden:
                continue

            if tokens + utt.tokens <= batchTokens:
                text += "\n" + Gpt3BotConversation.getLine(utt.speaker, utt.utterance)
            else:
                summary = await cls.__summarizer.summarize(text, mode="story")
                yield Gpt3BotSummary(summary, lastIdx, idx - 1)
                lastIdx = idx
                text = Gpt3BotConversation.getLine(utt.speaker, utt.utterance)

            summary = await cls.__summarizer.summarize(text, mode="story")
            yield Gpt3BotSummary(summary, lastIdx, len(utterances))

    def __init__(self,  summary: str, begin: int, end: int):
        self.summary = summary
        self.begin = begin
        self.end = end
        self.tokens = Gpt3Portal.estimateTokens(summary)


class Gpt3BotConversation:

    MIN_UTTERANCES = 6
    NARRATION = "NARRATION"

    def __init__(self, name: str, persona: List[str], utteranceLimit: int):
        self.name = name
        self.persona = "  ".join([self.__changeSubject(fact, name) for fact in persona]) if persona else []
        self.personaTokens = Gpt3Portal.estimateTokens(self.persona)
        self.conversation: List[Gpt3BotUtterance] = []
        self.summaries: List[Gpt3BotSummary] = []
        self.utteranceLimit = utteranceLimit
        self.currentUtteranceLimit = utteranceLimit

        self.me = "我" if any([Languages.isIdeography(c) for c in self.name]) else "Me"

        logging.info(f"Persona: {self.persona}")
        logging.info(f"Utterance limit: {self.utteranceLimit}")

    @classmethod
    def __changeSubject(cls, fact, name):

        fact = fact.replace("我", name)
        fact = fact.replace("你", "我")

        words = re.split("[ ,.!?]", fact)
        changed = []
        for word in words:
            if not word:
                continue

            changed.append(
                name if word == "I" or word == "me" else
                "is" if word == "am" else
                f"{name}'s" if word == "my" or word == "My" or word == "mine" else
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

        fact = fact.strip()
        fact = fact + ("" if fact.endswith(".") else ".")

        return fact

    def addUtterance(self, utterance: str, speaker: Optional[str] = None):
        if speaker is None:
            speaker = self.nextSpeaker()

        self.conversation.append(Gpt3BotUtterance(speaker, utterance))

    def getPrompt2(self, nextSpeaker: str = None):
        # TODO implement this
        pass

    def getPrompt(self, nextSpeaker: str = None):
        utterances = []
        for u in reversed(self.conversation):
            if not u.hidden:
                utterances.append(self.getLine(u.speaker, u.utterance))
                if len(utterances) > self.currentUtteranceLimit:
                    break
        utterances.reverse()

        if not nextSpeaker:
            nextSpeaker = self.name
        return "\n".join([self.persona, "========"] + utterances) + f"\n{nextSpeaker}: "

    def reset(self):
        self.conversation = []

    def restore(self, script: list):
        for utterance in script:
            m = re.match(r"\s*((\d+).)?\s*(\w+):\s*(.+)", utterance)
            if m:
                speaker = "Me" if m.group(3) == "You" else m.group(3)
                self.addUtterance(m.group(4), speaker=speaker)
                continue

            m = re.match(r"\s*((\d+).)?\s*\(\s*(.+)\s*\)", utterance)
            if m:
                self.addUtterance(m.group(3), speaker=self.NARRATION)
                continue

    def removeAi(self):
        self.conversation = [c for i, c in enumerate(self.conversation) if c.speaker == self.me]

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

        self.conversation = remain + self.conversation[indices[-1] + 1:]

    def redo(self):
        # Clear anything after and include the last utterance from the user
        try:
            while self.conversation[-1].speaker != self.me:
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
            if c.speaker != self.me and c.speaker != self.NARRATION:
                c.hidden = True

    def replace(self, utterance: str, idx: int = None):
        if idx is None:
            if len(self.conversation) == 0:
                self.addUtterance(utterance)
                return
            else:
                idx = -1

        self.conversation[idx].utterance = utterance

    def isSimilarToLast(self, speaker: str, utterance: str, threshold=0.6) -> bool:
        for u in reversed(self.conversation):
            if u.speaker == speaker:
                similarity = difflib.SequenceMatcher(None, utterance, u.utterance).ratio()
                if similarity > threshold:
                    logging.info(f"Too similar to previous.  Similarity: {similarity}  Threshold: {threshold}")
                    logging.info(f"    '{utterance}' vs '{u.utterance}'")
                    return True

        return False

    def nextSpeaker(self) -> str:
        if not self.conversation:
            return self.me
        return self.name if self.conversation[-1].speaker == self.me else self.me

    def length(self):
        return len(self.conversation)

    def getSpeaker(self, isUser: bool):
        return self.me if isUser else self.name

    def fewerUtterances(self, n: int = 2):
        if self.currentUtteranceLimit >= self.MIN_UTTERANCES + n:
            self.currentUtteranceLimit -= n
            logging.info(f"Lower number of utterances to {self.currentUtteranceLimit}")
            return self.currentUtteranceLimit
        else:
            logging.info(f"Cannot have any fewer utterances than {self.currentUtteranceLimit}")
            return None

    def promptMoreUtterances(self, n: int = 2):
        if self.currentUtteranceLimit <= self.utteranceLimit - n:
            self.currentUtteranceLimit += n
            logging.info(f"Raise number of utterances to {self.currentUtteranceLimit}")
            return self.currentUtteranceLimit
        else:
            return None

    @classmethod
    def getLine(cls, speaker: str, utterance: str) -> str:
        if speaker == cls.NARRATION:
            return f"{utterance}"
        else:
            return f"{speaker}: {utterance}"

