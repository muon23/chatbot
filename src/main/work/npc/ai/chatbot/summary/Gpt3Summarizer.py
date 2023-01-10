import logging
import os
import re
from typing import Optional

import openai
from iso639 import languages
# from ftlangdetect.detect import get_or_load_model, detect

from work.npc.ai.chatbot.summary.Summarizer import Summarizer
from work.npc.ai.utilities.Gpt3Portal import Gpt3Portal


class Gpt3Summarizer(Summarizer):
    __portal: Gpt3Portal = None

    __DEFAULT_TOKEN_LIMIT = 1000
    __DEFAULT_TEMPERATURE = 0.1

    __PROMPT = {
        "summary": "\n====\nSummarize the conversation above{language}.  Separate key points into paragraphs:\n",
        "digest": "\n====\nDigest the text above{language}, separating key points into multiple paragraphs:\n",
        "title": "\n====\nRecommend {numTitles} titles for the text above{language}:\n",
        "conclusion": "\n====\nWhat is the conclusion of the text above{language}:\n",
        "actions": "\n====\nList the action items from the text above{language}:\n",
        "todo": "\n====\n根据上面的对话创建一个提醒以及提醒时间、人物和主题，并判断主题属于哪个类别：0-开会，1-健身，2-学习，3-购物，4-聚会，5-其它:\n",
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

        # download fasttext language detect model
        # get_or_load_model()

    @classmethod
    def __getPrompt(cls, **kwargs) -> str:
        mode = kwargs.get("mode")
        numTitles = kwargs.get("numTitles")
        languageCode = kwargs.get("language")
        tone = kwargs.get("tone")

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

        # Put back text
        text = os.linesep.join([s for s in lines if s]) + cls.__getPrompt(**kwargs)

        return text

    async def summarize(self, text: str, **kwargs) -> str:
        if not text:
            return ""

        mode = kwargs.get("mode")
        prompt_param = kwargs.get("prompt")

        # if language is None:
        #     lang_detect = detect(text=text.replace("\n", " "), low_memory=False)
        #     language = lang_detect["lang"]

        if prompt_param and mode in ["todo", "reminder"]:
            prompt = "{}\n\n\n{}".format(text, prompt_param)
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
