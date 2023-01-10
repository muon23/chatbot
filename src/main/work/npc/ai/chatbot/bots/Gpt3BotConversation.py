import difflib
import logging
import re
from typing import List, Optional, Set

from work.npc.ai.chatbot.summary.Gpt3Summarizer import Gpt3Summarizer
from work.npc.ai.utilities.Gpt3Portal import Gpt3Portal
from work.npc.ai.utilities.Languages import Languages


class Gpt3BotUtterance:
    def __init__(self, speaker: str, utterance: str):
        if speaker == Gpt3BotConversation.NARRATION:
            # Narration needs to be surrounded by ( )
            if utterance[0] != "(":
                utterance = "(" + utterance
            if utterance[-1] != ")":
                utterance += ")"

        self.speaker = speaker
        self.utterance = utterance
        self.tokens = Gpt3Portal.estimateTokens(Gpt3BotConversation.getLine(speaker, utterance))


class Gpt3BotSummary:
    __summarizer = None

    @classmethod
    async def ofUtterances(cls, utterances: List[Gpt3BotUtterance], begin: int, end: int) -> Optional["Gpt3BotSummary"]:
        if not cls.__summarizer:
            cls.__summarizer = Gpt3Summarizer()

        if not utterances or begin >= end:
            return None

        text = "\n".join([
            Gpt3BotConversation.getLine(utt.speaker, utt.utterance) for utt in utterances[begin:end]
        ])

        summary = await cls.__summarizer.summarize(text, mode="story")
        summarized = Gpt3BotSummary(summary, begin, end)

        originalTokens = sum([u.tokens for u in utterances[begin:end]])
        ratio = summarized.tokens / originalTokens
        logging.info(f"Summarized utterances.  {summarized.tokens} / {originalTokens} = {ratio:4.2f}")
        return summarized

    @classmethod
    async def ofSummaries(cls, summaries: List["Gpt3BotSummary"]) -> Optional["Gpt3BotSummary"]:
        if not cls.__summarizer:
            cls.__summarizer = Gpt3Summarizer()

        if not summaries:
            return None
        if len(summaries) == 1:
            return summaries[0]

        begin = summaries[0].begin
        end = summaries[-1].end

        text = "\n".join([s.summary for s in summaries])

        summary = await cls.__summarizer.summarize(text, mode="story")
        summarized = Gpt3BotSummary(summary, begin, end)

        originalTokens = sum([s.tokens for s in summaries])
        ratio = summarized.tokens / originalTokens
        logging.info(f"Summarized summaries.  {summarized.tokens} / {originalTokens} = {ratio:4.2f}")
        return summarized

    def __init__(self,  summary: str, begin: int, end: int):
        self.summary = summary
        self.begin = begin
        self.end = end
        self.tokens = Gpt3Portal.estimateTokens(summary)


class Gpt3BotConversation:

    MIN_UTTERANCES = 6
    NARRATION = "NARRATION"

    def __init__(self, persona: List[str], **kwargs):
        self.name = kwargs.get("name")
        self.persona: List[str] = [self.__changeSubject(fact, self.name) for fact in persona]
        self.personaTokens: int = sum([Gpt3Portal.estimateTokens(fact) for fact in self.persona])
        self.conversation: List[Gpt3BotUtterance] = []
        self.summaries: List[Gpt3BotSummary] = []
        self.summaryTokens: int = 0
        self.activeUtteranceTokens: int = 0

        self.maxActiveUtteranceTokens: int = kwargs.get("maxActiveUtteranceTokens", 2000)
        self.maxTokens: int = kwargs.get("maxTokens", 3000)

        userChinese = any([Languages.isIdeography(c) for c in self.name])

        me = kwargs.get("you", None)   # For the bot, "you" is the user.
        self.me = me if me else "我" if userChinese else "I"
        self.you = "你" if userChinese else "You"

        self.replaceMe = None
        self.redoMark = 0

        logging.info(f"Persona: {self.persona}")

    @classmethod
    def __changeSubject(cls, fact, name):

        fact = fact.replace("我", name)
        fact = fact.replace("你", "我")

        words = re.findall(r"[\w']+|[.,!?;]", fact)
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
                f"{name} and I" if word in ["we", "We"] else
                word
            )
        fact = " ".join(changed)

        fact = re.sub(r'\s([.,!?;](?:\s|$))', r'\1', fact)
        fact = re.sub(r"I\s+are", "I am", fact)
        fact = re.sub(r"I\s+were", "I was", fact)

        fact = fact.strip()
        fact = fact + ("" if fact.endswith(".") else ".")

        return fact

    def __recalculateActiveUtteranceTokens(self):
        self.activeUtteranceTokens = sum(
            c.tokens for c in self.conversation[self.activeUtteranceStart():]
        )
        return self.activeUtteranceTokens

    async def addUtterance(self, utterance: str, speaker: Optional[str] = None):
        if speaker is None:
            speaker = self.nextSpeaker()

        if speaker == self.me:
            self.redoMark = self.length()
            if self.replaceMe:
                speaker = self.replaceMe
                self.replaceMe = None

        utt = Gpt3BotUtterance(speaker, utterance)
        self.conversation.append(utt)
        self.activeUtteranceTokens += utt.tokens
        await self.__summarizeIncrementally()

    async def __summarizeIncrementally(self):
        # If active utterance tokens exceeds limit, summarize 1/2 of the utterances
        while self.activeUtteranceTokens > self.maxActiveUtteranceTokens:
            # Figure from where to where to summarize
            summarizeBeginIdx = self.activeUtteranceStart()
            summarizeEndIdx = summarizeBeginIdx
            tokens2Summarize = self.maxActiveUtteranceTokens // 2
            self.activeUtteranceTokens -= tokens2Summarize
            while tokens2Summarize > 0:
                tokens2Summarize -= self.conversation[summarizeEndIdx].tokens
                summarizeEndIdx += 1
            self.activeUtteranceTokens += tokens2Summarize

            summary = await Gpt3BotSummary.ofUtterances(self.conversation, summarizeBeginIdx, summarizeEndIdx)
            self.summaries.append(summary)
            self.summaryTokens += summary.tokens

        # Calculate prompt tokens.  If exceeds limit, summarize the summaries.
        promptTokens = self.personaTokens + self.summaryTokens + self.activeUtteranceTokens
        while promptTokens >= self.maxTokens:
            logging.info(f"Prompt tokens ({promptTokens}) exceeds maximum prompt allowance ({self.maxTokens})")
            if len(self.summaries) < 2:
                # Cannot summarize further
                raise Gpt3Portal.TooManyTokensError("Token limit exceeded.  Cannot summarize any further.")

            toSummarize = int(max(len(self.summaries) // 2.5, 2))
            logging.info(f"Summarizing {toSummarize} summaries")
            summary = await Gpt3BotSummary.ofSummaries(self.summaries[:toSummarize])
            tokenDiff = sum(self.summaries[i].tokens for i in range(toSummarize)) - summary.tokens
            promptTokens -= tokenDiff
            self.summaries = [summary] + self.summaries[toSummarize:]
            self.summaryTokens -= tokenDiff

    async def summarize(self):
        self.summaries = []
        self.summaryTokens = 0
        self.__recalculateActiveUtteranceTokens()
        await self.__summarizeIncrementally()

    def getPrompt(self, nextSpeaker: str = None):
        activeUtteranceBegin = self.activeUtteranceStart()
        if not nextSpeaker:
            nextSpeaker = self.name

        logging.info(
            f"Number of tokens: persona={self.personaTokens}, summary={self.summaryTokens}, "
            f"utterance={self.activeUtteranceTokens} "
        )
        prompt = "\n".join(
            self.persona + ["===="] +
            [s.summary for s in self.summaries] +
            [self.getLine(u.speaker, u.utterance) for u in self.conversation[activeUtteranceBegin:]] +
            [f"\n{nextSpeaker}: "]
        )
        return prompt

    def reset(self):
        self.conversation = []
        self.summaries = []
        self.summaryTokens = 0
        self.activeUtteranceTokens = 0

    async def restore(self, script: list):
        for utterance in script:
            m = re.match(r"^\s*((\d+)\.)?\s*(\w+):\s*(.+)", utterance)
            if m:
                speaker = self.me if m.group(3) == self.you else m.group(3)
                await self.addUtterance(m.group(4), speaker=speaker)
                continue

            m = re.match(r"^\s*((\d+)\.)?\s*\(\s*([^()]+)\s*\)\s*$", utterance)
            if m:
                await self.addUtterance(f"({m.group(3)})", speaker=self.NARRATION)
                continue

    async def erase(self, indices: Set[int]):
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

        self.__recalculateActiveUtteranceTokens()
        activeUtteranceStart = self.activeUtteranceStart()
        if any([i < activeUtteranceStart for i in indices]):
            await self.summarize()

    def redo(self):
        # Clear anything after and include the last utterance from the user
        num2pop = self.length() - self.redoMark
        for _ in range(num2pop):
            self.conversation.pop()

    def __parseReplacement(self, replacement: str):
        m = re.match(r"^\s*((\d+)\.)?\s*\(\s*([^()]+)\s*\)\s*$", replacement)
        if m:
            idx = int(m.group(2)) if m.group(2) else None
            utterance = m.group(3) if m.group(3) else None
            return idx, self.NARRATION, utterance.strip()

        m = re.match(r"^\s*((\d+).)?\s*((\w+):)?\s*(.+)", replacement)
        if m:
            idx = int(m.group(2)) if m.group(2) else None
            speaker = None if not m.group(4) else self.me if m.group(4) == self.you else m.group(4)
            utterance = m.group(5) if m.group(5) else None
            return idx, speaker, utterance.strip()

        return None, None, None

    async def replace(self, replacement):
        needSummarize = False
        if not isinstance(replacement, list):
            replacement = [replacement]

        for r in replacement:
            if not isinstance(r, str):
                continue

            idx, speaker, utterance = self.__parseReplacement(r)
            if not utterance:
                continue

            if idx is None:
                if self.length() == 0:
                    await self.addUtterance(utterance)
                    return
                else:
                    idx = -1

            if speaker:
                self.conversation[idx].speaker = speaker
            self.conversation[idx].utterance = utterance
            self.conversation[idx].tokens = Gpt3Portal.estimateTokens(
                Gpt3BotConversation.getLine(self.conversation[idx].speaker, utterance)
            )

            if self.activeUtteranceStart() > idx >= 0:
                needSummarize = True

        if needSummarize:
            await self.summarize()

    async def script(self, script):
        nextSpeaker = self.nextSpeaker()
        if not isinstance(script, list):
            script = [script]

        for line in script:

            if not isinstance(line, str):
                continue

            _, speaker, utterance = self.__parseReplacement(line)
            if not utterance:
                continue

            if not speaker:
                speaker = nextSpeaker
            elif speaker == self.you:
                speaker = self.me

            await self.addUtterance(utterance=utterance, speaker=speaker)
            nextSpeaker = speaker

    async def insert(self, scripts):
        if not isinstance(scripts, list):
            await self.script(scripts)

        if isinstance(scripts[0], int):
            scripts = [scripts]

        needSummarize = False
        insertions = []
        for script in scripts:
            if not isinstance(script, list):
                await self.script(script)

            insertion = script.pop(0) if isinstance(script[0], int) else self.length()
            utterances = []
            for line in script:
                _, speaker, utterance = self.__parseReplacement(line)
                utterances.append(Gpt3BotUtterance(speaker, utterance))
            insertions.append((insertion, utterances))

            if self.activeUtteranceStart() > insertion >= 0:
                needSummarize = True

        insertions.sort(key=lambda x: x[0])
        inserted = []
        lastInsertion = 0
        for insertion in insertions:
            if insertion[0] == 0:
                inserted = insertion[1]
            else:
                inserted += self.conversation[lastInsertion:insertion[0]] + insertion[1]
                lastInsertion = insertion[0]

        inserted += self.conversation[lastInsertion:]
        self.conversation = inserted

        if needSummarize:
            await self.summarize()

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

    def activeUtteranceStart(self):
        return self.summaries[-1].end if self.summaries else 0

    def getSpeaker(self, isUser: bool):
        return self.me if isUser else self.name

    @classmethod
    def getLine(cls, speaker: str, utterance: str) -> str:
        if speaker == cls.NARRATION:
            return f"{utterance}"
        else:
            return f"{speaker}: {utterance}"
