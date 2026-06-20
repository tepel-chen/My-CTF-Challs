# NOTE: This hash is pinned to avoid version and environment differences.
FROM node:26.1.0-trixie-slim@sha256:4c987c825a40e2fe2179e9e14647d0432849934def25d7595e3ba3a8811d9b69

WORKDIR /app

COPY package.json ./
RUN npm install

COPY index.js ./
COPY views ./views/

CMD ["npm", "start"]
