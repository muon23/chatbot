FROM debian:buster-slim

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

RUN cd /app/chatbot/deployment \
    && apt-get update \
    && apt-get -y install python3.9 curl python3.9-distutils \
    && rm -f /usr/bin/python3 \
    && ln -s /usr/bin/python3.9 /usr/bin/python3 \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3 get-pip.py \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install -r requirements.txt --no-cache-dir \
    && python3 get-model.py "facebook/blenderbot-400M-distill" \
    && python3 get-model.py "facebook/blenderbot-1B-distill" \
    && python3 get-model.py "zoo:blender/blender_3B/model"

#    && chmod +x setup-pip.sh \
#    && ./setup-pip.sh \

WORKDIR /app/chatbot/deployment

# Volumes
VOLUME ["/app/store"]

# Application ports
EXPOSE 8080
EXPOSE 8081

# Start the default service
ENTRYPOINT []
CMD []
