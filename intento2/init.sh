#!/bin/bash

NUM_INSTANCES=$1
BROKER_IP=${2:-"localhost"}

if [ -z "$NUM_INSTANCES" ]; then
    echo "Starting 2 isnstances..."
    NUM_INSTANCES="2"
fi

pkill -f mosquitto
pkill -f prox2mqtt.py
pkill -f influxd
pkill -f telegraf
pkill -f api_sensores.py
sleep 1

trap "kill 0" EXIT

mosquitto -c mosquitto.conf &
sleep 2
influxd &
sleep 2
telegraf --config telegraf.conf &
sleep 2
uvicorn api_sensores:app --host 0.0.0.0 --port 8000 &
sleep 2

for i in $(seq 1 "$NUM_INSTANCES"); do
    PORT=$((8000 + i)) 
    python3 prox2mqtt.py --port "$PORT" --broker "$BROKER_IP" &
done

sleep 1
haproxy -f haproxy.cfg
