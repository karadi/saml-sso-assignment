#!/bin/sh
# Creates the two .env files with random secrets if they do not exist yet.
set -e
cd "$(dirname "$0")/.."
if [ ! -f authentik/.env ]; then
  { echo "PG_PASS=$(openssl rand -hex 24)"; echo "AUTHENTIK_SECRET_KEY=$(openssl rand -hex 48)"; } > authentik/.env
  echo "Created authentik/.env"
fi
if [ ! -f sample-app/.env ]; then
  { echo "FLASK_SECRET_KEY=$(openssl rand -hex 32)"
    echo "SP_BASE_URL=https://localhost:5443"
    echo "IDP_METADATA_FILE=/idp/idp_metadata.xml"; } > sample-app/.env
  echo "Created sample-app/.env"
fi
echo "Done. Next: docker compose up -d"
