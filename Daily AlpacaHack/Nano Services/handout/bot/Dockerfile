FROM node:26.1.0-trixie-slim
ENV PUPPETEER_SKIP_DOWNLOAD=true
WORKDIR /bot

RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
USER node
CMD [ "node", "index.js" ]
