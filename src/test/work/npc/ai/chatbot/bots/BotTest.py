import unittest

from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


class BotTest(unittest.TestCase):
    def test_transformer(self):
        alice = TransformerBot(
            "Alice",
            persona=["I am a woman", "I am 28 years old", "I live in San Francisco", "I like to swim"],
        )
        print(alice.respondTo("Hello.  Where do you live?", True))
        print(alice.respondTo("How nice.  What do you do for fun?", True))
        print(alice.respondTo("I like painting.  By the way, my name is CJ.  May I have your name?", True))

        self.assertTrue(True)

    def test_parlai(self):
        alice = ParlaiBot(
            "Alice",
            persona=["I am a woman", "I am 28 years old", "I live in San Francisco", "I like to swim"],
            # modelName="zoo:bb3/bb3_3B/model"
        )
        print(alice.respondTo("Hello.  Where do you live?", True))
        print(alice.respondTo("How nice.  What do you do for fun?", True))
        print(alice.respondTo("I like painting.  By the way, my name is CJ.  May I have your name?", True))

        self.assertTrue(True)
