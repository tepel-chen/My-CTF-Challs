FROM node:22.9.0-slim as app

WORKDIR /app
COPY package* .
RUN npm i

FROM pwn.red/jail
COPY --from=app / /srv

COPY --chmod=755 index.js /srv/app/
COPY --chmod=755 run.sh /srv/app/run
COPY --chmod=444 flag.txt /srv/app/
ENV JAIL_MEM=64M JAIL_PIDS=20 JAIL_TMP_SIZE=1M