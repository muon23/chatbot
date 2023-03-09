import logging
import os
import re
from typing import Dict, List

import openai
from iso639 import languages

from cj.chatbot.summary.Summarizer import Summarizer
from cj.utilities.Gpt3Portal import Gpt3Portal


class Gpt3Summarizer(Summarizer):
    __portal: Gpt3Portal = None

    __DEFAULT_TOKEN_LIMIT = 1000
    __DEFAULT_TEMPERATURE = 0.1

    __PROMPT = {
        "summary": "\n====\nSummarize the above{language}:\n",
        "title": "\n====\nRecommend {numTitles} for the text above{language}:\n",
        "conclusion": "\n====\nWhat is the conclusion of the text above{language}:\n",
        "actions": "\n====\nList the action items from the text above{language}:\n",
        "reminder": "\n====\nSet a reminder from the text above{language} with the time of the event:\n",
        "story": "\n====\nSummarize the section of a story above:\n",
        "rewrite": "\n====\nRewrite the text above{tone}{language}:\n",
    }

    @classmethod
    def of(cls, model: str) -> Summarizer:
        return Gpt3Summarizer() if model == "gpt3" else None

    def __init__(self):

        if not self.__portal:
            accessKey = os.environ.get("OPENAI_KEY")
            if not accessKey:
                raise RuntimeError("Environment OPENAI_KEY not defined")

            self.__portal = Gpt3Portal.of(accessKey)

    @classmethod
    def __getPrompt(cls, **kwargs) -> str:
        mode = kwargs.get("mode", "summary")
        numTitles = kwargs.get("numTitles", 1)
        languageCode = kwargs.get("language", None)
        tone = kwargs.get("tone", None)

        if languageCode:
            try:
                languageName = languages.get(alpha2=languageCode).name
            except KeyError:
                raise RuntimeError(f"Invalid language code '{languageCode}'")

            language = f" using {languageName}"
        else:
            language = ""

        tone = f" with a {tone} tone" if tone else ""

        prompt = cls.__PROMPT.get(mode, None)
        if not prompt:
            raise RuntimeError(f"Mode {mode} not supported")

        return prompt.format(language=language, numTitles=numTitles, tone=tone)

    @classmethod
    def __cleanUpText(cls, text: str, **kwargs) -> str:

        # Remove empty lines and leading and trailing spaces
        lines = [s.strip() for s in text.splitlines()]

        mode = kwargs.get("mode")
        if mode in ["title", "digest"]:
            # Remove speakers
            lines = [s for s in lines if not re.match(r"[^:]*:$", s)]

        # Remove timestamps
        lines = [s for s in lines if not re.match(r"\d{2}:\d{2}$", s)]

        # numTitles optimize
        numTitles = kwargs.get("numTitles", 1)
        kwargs["numTitles"] = f"a title" if numTitles == 1 else f"{numTitles} titles"

        # Put back text
        text = os.linesep.join([s for s in lines if s]) + cls.__getPrompt(**kwargs)

        return text

    @classmethod
    def __cleanUpDialog(cls, dialog: List[Dict[str, str]], **kwargs) -> str:

        mode = kwargs.get("mode")
        speakers = set()
        text = ""

        for line in dialog:
            try:
                speaker = line.get("speaker")
                utterances = line.get("utterances")
            except KeyError:
                continue   # Ignore anything without these fields

            if not isinstance(utterances, list):
                utterances = [utterances]

            replyToSpeaker = line.get("replyToSpeaker", None)
            replyToUtterance = line.get("replyToUtterance", "")

            replyTo = f"(in reply to {replyToSpeaker}: {replyToUtterance[:20]}...)" if replyToSpeaker else ""

            spoken = os.linesep.join(utterances)
            spoken = re.sub(r"@\[([^]]+)]", r"(to \1)", spoken)

            speakers.add(speaker)

            if mode in ["title", "digest"]:
                text += f"{spoken}\n"
            else:
                text += f"{speaker}: {replyTo} {spoken}\n\n"

        speakers = list(speakers)
        numSpeakers = len(speakers)
        if numSpeakers <= 1:
            group = f"talk from {speakers[0]}"
        elif numSpeakers == 2:
            group = f"conversation between {speakers[0]} and {speakers[1]}"
        else:
            group = f"conversation amongst {', '.join(speakers[:-1])} and {speakers[-1]}"

        # numTitles optimize
        numTitles = kwargs.get("numTitles", 1)
        kwargs["numTitles"] = f"a title" if numTitles == 1 else f"{numTitles} titles"

        text = os.linesep.join([
            f"Consider the following conversation {group}:",
            "~~~",
            text,
            "~~~",
            cls.__getPrompt(**kwargs)
        ])

        return text

    async def summarize(self, **kwargs) -> str:
        text = kwargs.pop("text", "")
        if isinstance(text, list):
            text = "\n".join(text)
        dialog = kwargs.pop("dialog", [])
        mode = kwargs.get("mode")
        prompt_param = kwargs.get("prompt")

        if prompt_param and mode in ["todo", "reminder"]:
            prompt = "{}\n\n\n{}".format(text, prompt_param)
        elif dialog:
            prompt = self.__cleanUpDialog(dialog, **kwargs)
        else:
            prompt = self.__cleanUpText(text, **kwargs)
        logging.info(f"Prompt = \n{prompt}")

        try:
            response = await self.__portal.complete(
                prompt=prompt,
                retries=5,
                temperature=self.__DEFAULT_TEMPERATURE,
                max_tokens=self.__DEFAULT_TOKEN_LIMIT
            )

            response = response[0]
            logging.info(f">>>> OpenAI response:\n{response}")

        except openai.error.InvalidRequestError as e:
            raise RuntimeError(f"Content exceeds max number of words.  Please split into shorter contents.")

        return response
