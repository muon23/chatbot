#!/bin/bash

set -x

export DEBIAN_FRONTEND=noninteractive
export TZ=${TZ:-"Etc/UTC"}

apt-get update
apt-get -y install python3.9
apt-get -y install python3.9-distutils
apt-get -y install curl

rm -f /usr/bin/python3
ln -s /usr/bin/python3.9 /usr/bin/python3

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install -r requirements.txt --no-cache-dir

python3 get-model.py "facebook/blenderbot-400M-distill"
python3 get-model.py "facebook/blenderbot-1B-distill"
python3 get-model.py "facebook/blenderbot-3B"

set +x