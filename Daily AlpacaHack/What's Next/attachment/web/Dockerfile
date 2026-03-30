FROM node:25.8.0-trixie-slim

WORKDIR /app

COPY package*.json ./
RUN npm i --omit=dev

COPY . .

RUN mv src/pages/secret.js src/pages/secret-$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32).js
RUN npm run build
CMD [ "npm", "start" ]