import unittest

from work.npc.ai.chatbot.bots.Bot import Bot


class BotTest(unittest.TestCase):
    def test_basic(self):
        alice = Bot("Alice", persona=["I am a woman", "I am 28 years old", "I live in San Francisco", "I like to swim"])
        print(alice.respondTo("Hello.  Where do you live?", True))
        print(alice.respondTo("How nice.  What do you do for fun?", True))
        print(alice.respondTo("I like painting.  By the way, my name is CJ.  May I have your name?", True))
