#!/bin/sh
set -e
if [ ! -f /certs/server.crt ]; then
  echo "Generating self-signed certificate for localhost..."
  openssl req -x509 -nodes -newkey rsa:2048 -sha256 -days 365 \
    -keyout /certs/server.key -out /certs/server.crt \
    -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost"
fi
exec gunicorn --certfile /certs/server.crt --keyfile /certs/server.key \
  -b 0.0.0.0:5443 --access-logfile - app:app
