import os
import sys
# from pyapollo.apollo_client import ApolloClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/main')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../commons/src/main')))

from cj.chatbot.api.ChatBotServer import ChatBotServer
from dotenv import load_dotenv

os.environ["CHATBOT_PROJECT_ROOT"] = os.path.abspath("..")
projectRoot = os.environ.get("CHATBOT_PROJECT_ROOT")

if len(sys.argv) < 2:
    print("Running environment required.  ('local', 'dev', 'uat', or 'prod')")
    exit(1)

environment = sys.argv[1]
load_dotenv(f"{projectRoot}/deployment/{sys.argv[1]}/environment")

if environment != "local":
    # Get OPNEAI_KEY from Apollo when running in the cloud
    app_id = os.environ.get("APP_ID")
    config_server_url = os.environ.get("CONFIG_SERVER_URL")
    authorization = os.environ.get("AUTHORIZATION")
    cache_file_path = os.environ.get("CACHE_FILE_PATH")
    env = os.environ.get("ENV")
    namespace = os.environ.get("NAMESPACE")
    openai_key = os.environ.get("OPENAI_KEY")

    # client = ApolloClient(
    #     app_id=app_id,
    #     config_server_url=config_server_url,
    #     authorization=authorization,
    #     cache_file_path=cache_file_path,
    #     env=env
    # )
    # client.start()
    #
    # os.environ["OPENAI_KEY"] = client.get_value(openai_key, "default", namespace)

ChatBotServer.main(debugArgs=["-c", f"{projectRoot}/deployment/{environment}/chatbot.yml"])
