#!/bin/sh
cd "$(dirname "$0")/.."
python3 tools/unsigned.py
docker compose logs --tail 3
