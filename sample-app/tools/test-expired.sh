#!/bin/sh
cd "$(dirname "$0")/.."
cp tools/expired_response.txt tools/captured_response.txt
python3 tools/replay.py replay
docker compose logs --tail 3
