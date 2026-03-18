FROM node:25.2.1-bookworm-slim

WORKDIR /app

COPY package*.json ./
RUN npm i --omit=dev

COPY . .

USER node

CMD [ "node", "index.js" ]