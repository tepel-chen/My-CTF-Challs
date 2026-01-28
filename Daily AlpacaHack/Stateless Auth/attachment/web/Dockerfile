FROM python:3.14.2-slim-trixie

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+w /app/static
USER nobody

CMD flask run --host=0.0.0.0 --port=3000