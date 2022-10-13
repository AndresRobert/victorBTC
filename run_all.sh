#!/usr/bin/env bash

python3 ./src/counter.py > counter.log & echo $! & python3 ./src/server.py & echo $!