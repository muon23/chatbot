import unittest

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

    def test_gpt3_goodResponse(self):
        bot = Gpt3Bot()
        testStr = " yes.  (pent pent).  I can't run that fast!\n slow down\\n please!"
        result = bot._Gpt3Bot__isGoodResponse(testStr)
        print(result)
        self.assertEqual(len(testStr) - 2, len(result))


if __name__ == '__main__':
    unittest.main()
