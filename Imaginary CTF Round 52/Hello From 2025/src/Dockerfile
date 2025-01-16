FROM node:22.11.0-bookworm-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN mv flag.txt /flag-$(md5sum flag.txt | cut -c-32).txt
CMD ["npx", "nodemon", "app.js"]