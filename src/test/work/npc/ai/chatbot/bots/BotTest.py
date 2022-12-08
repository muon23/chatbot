import unittest
import asyncio

from work.npc.ai.chatbot.bots.Gpt3Bot import Gpt3Bot
from work.npc.ai.chatbot.bots.ParlaiBot import ParlaiBot
from work.npc.ai.chatbot.bots.TransformerBot import TransformerBot


class BotTest(unittest.TestCase):

    __testPersona = ["I am a woman", "I am 28 years old", "I live in San Francisco", "I like jogging"]

    async def __runBot(self, bot):
        utterances = [
            "Hello.  Where do you live?",
            "How nice.  What do you do for fun?",
            "I like painting.  By the way, my name is CJ.  May I have your name?"
        ]

        for utt in utterances:
            print(f">>> {utt}")
            print(await bot.respondTo(utt))

        conversation = list(bot.getConversation())
        print(conversation)
        self.assertEqual(len(conversation), 6)

    def test_transformer(self):
        bot = TransformerBot(persona=self.__testPersona)
        asyncio.run(self.__runBot(bot))

        pp = bot.getPersona()
        print(pp)
        for p in self.__testPersona:
            self.assertTrue(p in pp)

    def test_parlai(self):
        bot = ParlaiBot(
            persona=self.__testPersona,
            # modelName="zoo:bb3/bb3_3B/model"
        )
        asyncio.run(self.__runBot(bot))

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
        asyncio.run(self.__runBot(bot))

    def test_gpt3_goodResponse(self):
        bot = Gpt3Bot()
        testStr = " yes.  (pent pent).  I can't run that fast! slow down\\n please!"
        speaker, result = bot.parseUtterance(testStr)
        print(speaker, result)
        self.assertEqual(len(testStr) - 2, len(result))

        testStr = """Well, yes.  This world is in danger because of the black hole.
Me: The black hole?  I don't understand.
"""
        spoken, result = bot.processResponse(testStr, "Alice")
        print(result[0])
        self.assertEqual(len(result), 1)
        self.assertLess(len(result[0]), len(testStr)-30)
        self.assertEqual({"Alice"}, spoken)

        testStr = """............................
==========
(one week later)
        """
        spoken, result = bot.processResponse(testStr)
        print(result)
        self.assertEqual(result[0], "NARRATION: (one week later)")

        testStr = """(she walked to Emma, held her hand and shook it) Hello there.
Emma: Hello.  I am Emma.  Glad to meet you.  You are adorable.
April: I am April.  I am the most happy girl on the planet."""

        spoken, result = bot.processResponse(testStr, "April")
        print(spoken, result)

    def test_trouble(self):
        bot = Gpt3Bot()
        testStr = """I am so sorry, Mike.  I did not know they were spying on us.
Cindy:  It is OK.  We love April and Mike, too.  And we are happy that you have accepted us as part of the family.  April, would you like to be a centaur?
April:  I don't think I am comfortable with that.  I like to be a fox girl.  Um...  I am not sure about this.
"""
        spoken, result = bot.processResponse(testStr, "April")
        print(result)
        print(spoken)

    def test_gpt3_modifyConversation(self):
        bot = Gpt3Bot()

        # Test script
        instr1 = {
            "script": [
                "Her: aaa",
                "Me: bbb",
                "(fff)",
                "Her: ggg",
                "Me: hhh",
                "Tom: iii"
            ]
        }

        bot.modifyConversation(instr1)
        conv1 = list(bot.getConversation())
        print(conv1)
        self.assertEqual(len(conv1), len(instr1.get("script")))

        indices = list(bot._Gpt3Bot__makeIndices([7, "4", ":2", "18:", "9:11", "19:100"], 20))
        print(indices)
        self.assertEqual(set(indices), {4, 7, 0, 1, 2, 18, 19, 9, 10, 11})

        # Test hide and replace last
        hide = [":1", 5]
        instr2 = {
            "replace": "iii-replaced",
            "hide": hide
        }
        bot.modifyConversation(instr2)
        conv2 = list(bot.getConversation())
        print(conv2)
        hideIndices = set(bot._Gpt3Bot__makeIndices(hide, 20))
        for i, c in enumerate(conv2):
            if i in hideIndices:
                self.assertIn("hidden", c)
            else:
                self.assertNotIn("hidden", c)

        self.assertEqual(len(conv2), len(conv1))
        self.assertIn(instr2.get("replace"), conv2[-1])

        # Test show and replace with index
        show = ["0", "3:"]
        replaceStr = "ggg-replaced"
        instr3 = {
            "replace": f"3: {replaceStr}",
            "show": show
        }
        bot.modifyConversation(instr3)
        conv3 = list(bot.getConversation())
        print(conv3)
        showIndices = set(bot._Gpt3Bot__makeIndices(show, len(conv3)))
        for i, c in enumerate(conv3):
            if i in showIndices:
                self.assertNotIn("hidden", c)

        self.assertEqual(len(conv3), len(conv1))
        self.assertIn(replaceStr, conv3[3])

        instr4 = {
            "redo": 1,
            "erase": ["-1", 5]
        }
        bot.modifyConversation(instr4)
        conv4 = list(bot.getConversation())
        print(conv4)
        self.assertEqual(len(conv4), 2)
        self.assertEqual(conv4[0], "(fff)")

        bot.modifyConversation({**instr1, "hide_ai": True})
        conv5 = list(bot.getConversation())
        print(conv5)
        self.assertIn("hidden", conv5[1])

        bot.modifyConversation({"hide_ai": True})
        conv6 = list(bot.getConversation())
        print(conv6)
        for c in conv6:
            if "You" in c:
                self.assertFalse("hidden" in c)

        bot.modifyConversation({"remove_ai": True})
        conv7 = list(bot.getConversation())
        print(conv7)
        self.assertTrue(all([c[0] for c in conv7]))

        bot.modifyConversation({"erase": "1-2"})
        conv8 = list(bot.getConversation())
        print(conv8)


if __name__ == '__main__':
    unittest.main()
