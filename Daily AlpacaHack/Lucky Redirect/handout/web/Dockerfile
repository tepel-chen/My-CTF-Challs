# NOTE: This hash is pinned to avoid version and environment differences.
FROM python:3.14.6-slim-trixie@sha256:63a4c7f612a00f92042cbdcc7cdc6a306f38485af0a200b9c89de7d9b1607d15

WORKDIR /app

RUN pip install --no-cache-dir Flask==3.1.3

COPY app.py ./

CMD ["python", "app.py"]
