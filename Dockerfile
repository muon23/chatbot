FROM 587070264874.dkr.ecr.us-west-2.amazonaws.com/base-muon-chatbot:v1.0.0

RUN apt-get update
RUN apt-get install --no-install-recommends --yes build-essential
# Environment variables
ENV CHATBOT_BASE_PATH=/muon
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
RUN pip3 install --no-cache-dir zhon==1.1.5
RUN pip3 install --no-cache-dir sanic-cors==2.2.0
RUN pip3 install --no-cache-dir iso-639==0.4.5
RUN pip3 install --no-cache-dir apollo-client==2.1.2
RUN pip3 install --no-cache-dir fasttext-langdetect==1.0.3
RUN pip3 install --no-cache-dir wget==3.2
