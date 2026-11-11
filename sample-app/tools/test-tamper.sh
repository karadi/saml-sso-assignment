#!/bin/sh
cd "$(dirname "$0")/.."
pbpaste > tools/captured_response.txt
python3 tools/replay.py tamper
docker compose logs --tail 3
