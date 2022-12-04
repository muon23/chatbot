import logging
import os
import re
import time
from typing import Optional
from iso639 import languages

import openai

from work.npc.ai.chatbot.summary.Summarizer import Summarizer


class Gpt3Summarizer(Summarizer):
    completion = None

    DEFAULT_TOKEN_LIMIT = 3000
    DEFAULT_TEMPERATURE = 0.2

    @classmethod
    def of(cls, model: str) -> Summarizer:
        return Gpt3Summarizer() if model == "gpt3" else None

    def __init__(self):
        if not self.completion:
            accessKey = os.environ.get("OPENAI_KEY")
            if not accessKey:
                raise RuntimeError("Environment OPENAI_KEY not defined")

            try:
                openai.api_key = accessKey
                self.completion = openai.Completion()
            except Exception as e:
                raise RuntimeError(f"Cannot access GPT-3. {str(e)}")

    @classmethod
    def __cleanUpText(cls, text: str, mode: str, numTitles: int, language: Optional[str]) -> str:

        # Remove empty lines and leading and trailing spaces
        lines = [s.strip() for s in text.splitlines()]

        if mode in ["title", "digest"]:
            # Remove speakers
            lines = [s for s in lines if not re.match(r"[^:]*:$", s)]

        # Remove timestamps
        lines = [s for s in lines if not re.match(r"\d{2}:\d{2}$", s)]

        # Put back text
        text = os.linesep.join([s for s in lines if s])

        if language:
            try:
                languageName = languages.get(alpha2=language).name
            except KeyError:
                raise RuntimeError(f"Invalid language code '{language}'")

            language = f" using {languageName}"

        if mode == "summary":
            text += f"\n====\nSummarize the text above{language}:\n"
        elif mode == "digest":
            text += f"\n====\nDigest the text above{language}:\n"
        elif mode == "title":
            text += f"\n====\nRecommend {numTitles} titles for the text above{language}:\n"
        elif mode == "conclusion":
            text += f"\n====\nWhat is the conclusion of the text above{language}:\n"

        return text

    def summarize(self, text: str, **kwargs) -> str:
        if not text:
            return ""

        mode = kwargs.get("mode", "summarize")
        numTitles = kwargs.get("numTitles", 3)
        language = kwargs.get("language", None)

        prompt = self.__cleanUpText(text, mode, numTitles, language)
        logging.info(f"Prompt = \n{prompt}")
        response = None

        tries = 0
        while not response:
            try:
                response = self.completion.create(
                    prompt=prompt,
                    engine="text-davinci-003",
                    # engine="davinci",
                    stop=None,
                    temperature=self.DEFAULT_TEMPERATURE,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                    best_of=1,
                    max_tokens=self.DEFAULT_TOKEN_LIMIT
                )
                response = response.choices[0].text.strip()
                logging.info(f">>>> OpenAI response:\n{response}")

            except (
                    openai.error.APIConnectionError,
                    openai.error.RateLimitError,
                    AttributeError
            ) as e:
                tries += 1
                if tries > 5:
                    raise RuntimeError(f"GPT-3 access failed after {tries} tries.  Please try later.")

                logging.warning(f"GPT-3 access failure: {str(e)} {tries}")
                time.sleep(1)

            except openai.error.InvalidRequestError as e:
                raise RuntimeError(f"Content exceeds max number of words.  Please split into shorter contents.")

        return response
