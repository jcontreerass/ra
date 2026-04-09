#!/bin/bash

SERVER1_PATH="./server1/app.js"
SERVER2_PATH="./server2/app.js"

node $SERVER1_PATH &
node $SERVER2_PATH
