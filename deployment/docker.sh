#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

docker run -it --rm \
  --name chatbot \
  --mount type=bind,source="${SCRIPT_DIR}"/..,target=/root/chatbot \
  --mount type=bind,source="${SCRIPT_DIR}"/../../commons,target=/root/commons \
  -p 8080:8080 \
  -p 8081:8081 \
  ubuntu

