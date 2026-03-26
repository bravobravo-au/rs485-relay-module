#!/bin/bash
cd /home/brad/rs485-relay-module
source ./venv/bin/activate
for (( ; ; ))
do
  python mqtt.py --debug INFO
  sleep 10
done
