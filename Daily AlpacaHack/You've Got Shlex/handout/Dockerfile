# NOTE: This hash is pinned to avoid version and environment differences.
FROM python:3.14.6-slim-trixie@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -yq socat && rm -rf /var/lib/apt/lists/*

COPY flag.txt /flag.txt
COPY jail.py .

USER nobody:nogroup
CMD ["socat", "-T60", "TCP-L:1337,fork,reuseaddr", "EXEC:'python jail.py',stderr"]
