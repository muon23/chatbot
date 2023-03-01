#!/bin/bash

set -x

export DEBIAN_FRONTEND=noninteractive
export TZ=${TZ:-"Etc/UTC"}

apt-get update
apt-get -y install python3.10
apt-get -y install python3.10-distutils

rm -f /usr/bin/python3
ln -s /usr/bin/python3.10 /usr/bin/python3

alias pip='python3 -m pip'

pip install -U pip
pip install -U setuptools
pip install -r requirements.txt --no-cache-dir

#python3 get-model.py "facebook/blenderbot-400M-distill"
#python3 get-model.py "facebook/blenderbot-1B-distill"
#python3 get-model.py "facebook/blenderbot-3B"
python3 get-model.py "gpt2tokenizer"

set +x