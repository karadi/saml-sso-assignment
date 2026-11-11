FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config openssl zlib1g-dev \
    libxml2-dev libxslt1-dev libxmlsec1-dev libxmlsec1-openssl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# Build lxml and xmlsec from source so they link against the same libxml2
RUN pip install --no-cache-dir --no-binary lxml,xmlsec -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 5443
ENTRYPOINT ["./entrypoint.sh"]
