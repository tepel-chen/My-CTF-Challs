# NOTE: This hash is pinned to avoid version and environment differences.
FROM node:26.1.0-trixie-slim@sha256:4c987c825a40e2fe2179e9e14647d0432849934def25d7595e3ba3a8811d9b69
ENV PUPPETEER_SKIP_DOWNLOAD=true
WORKDIR /bot

RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
USER node
CMD [ "node", "index.js" ]
