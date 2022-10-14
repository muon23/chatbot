import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/main')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../commons/src/main')))

from work.npc.ai.chatbot.api.ChatBotServer import ChatBotServer


os.environ["CHATBOT_PROJECT_ROOT"] = os.path.abspath("..")

projectRoot = os.environ.get("CHATBOT_PROJECT_ROOT")

if len(sys.argv) < 2:
    print("Running environment required.  ('dev', 'uat', or 'prod')")
    exit(1)

ChatBotServer.main(debugArgs=["-c", f"{projectRoot}/deployment/{sys.argv[1]}/chatbot.yml"])
