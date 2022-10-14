import unittest

from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


class BotTest(unittest.TestCase):

    def __runBot(self, bot):
        print(bot.respondTo("Hello.  Where do you live?", True))
        print(bot.respondTo("How nice.  What do you do for fun?", True))
        print(bot.respondTo("I like painting.  By the way, my name is CJ.  May I have your name?", True))

        conversation = list(bot.getConversation())
        print(conversation)
        self.assertEqual(len(conversation), 6)

        pp = bot.getPersona()
        print(pp)
        for p in bot.persona:
            self.assertTrue(p in pp)

    def test_transformer(self):
        bot = TransformerBot(persona=["I am a woman", "I am 28 years old", "I live in San Francisco", "I like jogging"])
        self.__runBot(bot)

    def test_parlai(self):
        bot = ParlaiBot(
            persona=["I am a woman", "I am 28 years old", "I live in San Francisco", "I like to swim"],
            # modelName="zoo:bb3/bb3_3B/model"
        )

        self.__runBot(bot)


if __name__ == '__main__':
    unittest.main()
