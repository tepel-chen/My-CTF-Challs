# NOTE: This hash is pinned to avoid version and environment differences.
FROM python:3.14.6-slim-trixie@sha256:5ab1b2545ab88461c5fec78e00d6c3356de2a7446805b982d7c2061ece6ee49f

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=555 entrypoint.sh /entrypoint.sh
COPY init_db.py init_db.py
COPY app.py app.py

USER nobody

CMD ["/entrypoint.sh"]