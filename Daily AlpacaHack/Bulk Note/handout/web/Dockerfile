# NOTE: This hash is pinned to avoid version and environment differences.
FROM node:25.9.0-trixie-slim@sha256:46c2e03fa9f715d1568ebf054e27d2cf74d4c0897f2ad1763ae571d27190dfdd

WORKDIR /app

COPY package*.json ./
RUN npm i --omit=dev

COPY . .

USER node

CMD [ "node", "index.js" ]