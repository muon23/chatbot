import unittest

from cj.chatbot.api.ChatBotServer import ChatBotServer


class ChatHandlerTest(unittest.TestCase):

    def test_basic(self):

        ChatBotServer.main(debugArgs=["-c", "../../../../../../../deployment/local/chatbot.yml"])

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
