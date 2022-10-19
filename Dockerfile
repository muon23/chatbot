FROM 587070264874.dkr.ecr.us-west-2.amazonaws.com/base-tanka-chatbot:v1.0.0

# Environment variables
ENV CHATBOT_BASE_PATH=/tankasbot
ENV CHATBOT_SERVER_PORT=8080
ENV CHATBOT_PROJECT_ROOT="/app/chatbot"
ENV COMMONS_PROJECT_ROOT="/app/commons"
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

WORKDIR /app

COPY ./deployment /app/chatbot/deployment
COPY ./src /app/chatbot/src
COPY ./commons /app/commons

WORKDIR /app/chatbot/deployment

# Volumes
VOLUME ["/app/store"]

# Start the default service
ENTRYPOINT []
CMD []

# install required packages from PyPI
RUN pip3 install --no-cache-dir torch==1.12.1
RUN pip3 install --no-cache-dir sanic==21.9.1
RUN pip3 install --no-cache-dir nltk==3.7
RUN pip3 install --no-cache-dir numpy==1.23.3
RUN pip3 install --no-cache-dir transformers==4.23.1
RUN pip3 install --no-cache-dir typing==3.7.4.3
RUN pip3 install --no-cache-dir lrparsing~=1.0.13
RUN pip3 install --no-cache-dir parlai==1.7.1
RUN pip3 install --no-cache-dir bson==0.5.10
RUN pip3 install --no-cache-dir python-dotenv==0.21.0
RUN pip3 install --no-cache-dir openai==0.23.1
RUN pip3 install --no-cache-dir zhon==1.1.5
