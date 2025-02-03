FROM python:3.13.0-alpine3.20

ARG FLAG="ictf{fake_flag}"

WORKDIR /app

RUN echo "$FLAG" > /flag.txt
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]