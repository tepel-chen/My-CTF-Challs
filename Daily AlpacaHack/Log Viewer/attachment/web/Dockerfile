FROM python:3.13.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flag.txt /flag.txt
RUN mv /flag.txt /flag-$(md5sum /flag.txt | awk '{print $1}').txt

COPY . .

USER nobody

CMD flask run --host=0.0.0.0 --port=3000