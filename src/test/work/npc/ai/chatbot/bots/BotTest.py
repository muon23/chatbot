import os
import unittest

import openai

from work.npc.ai.chatbot.bots.Gpt3Bot import Gpt3Bot
from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


class BotTest(unittest.TestCase):

    __testPersona = ["I am a woman", "I am 28 years old", "I live in San Francisco", "I like jogging"]

    def __runBot(self, bot):
        utterances = [
            "Hello.  Where do you live?",
            "How nice.  What do you do for fun?",
            "I like painting.  By the way, my name is CJ.  May I have your name?"
        ]

        for utt in utterances:
            print(f">>> {utt}")
            print(bot.respondTo(utt))

        conversation = list(bot.getConversation())
        print(conversation)
        self.assertEqual(len(conversation), 6)

    def test_transformer(self):
        bot = TransformerBot(persona=self.__testPersona)
        self.__runBot(bot)

        pp = bot.getPersona()
        print(pp)
        for p in self.__testPersona:
            self.assertTrue(p in pp)

    def test_parlai(self):
        bot = ParlaiBot(
            persona=self.__testPersona,
            # modelName="zoo:bb3/bb3_3B/model"
        )
        self.__runBot(bot)

        pp = bot.getPersona()
        print(pp)
        for p in self.__testPersona:
            self.assertTrue(p in pp)

    def test_gpt3(self):
        bot = Gpt3Bot(
            persona=self.__testPersona,
            name="Alice"
            # modelName="zoo:bb3/bb3_3B/model"
        )

        print(bot.getPersona())
        self.__runBot(bot)

    def test_gpt3_access(self):
        openai.api_key = os.environ.get("MY_OPENAI_KEY")
        print(openai.api_key)
        completion = openai.Completion()

        prompt = (
            "Alice live in New York City.\n"
            "Alice like cheese.\n"
            "Alice like to swim.\n"
            "Alice is a woman.\n"
            "Alice's mother is an Italian.\n"
            "\n"
            "YOU: Hi.  Long time no see.  How are you doing?\n"
            "Alice:"
        )

        print(prompt)
        response = completion.create(
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
        reply = response.choices[0].text.strip().replace("//n", "/n")

        print(reply)


if __name__ == '__main__':
    unittest.main()
