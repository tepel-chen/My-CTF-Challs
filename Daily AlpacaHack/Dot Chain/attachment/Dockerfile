FROM node:25.7.0
WORKDIR /app
RUN apt-get update && apt-get install -yq socat

COPY *.js .

USER nobody:nogroup
CMD ["socat", "-T30", "tcp-listen:1337,fork,reuseaddr", "exec:'node jail.js',stderr"]
