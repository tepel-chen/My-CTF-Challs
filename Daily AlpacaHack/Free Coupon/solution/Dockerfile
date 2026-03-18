FROM python:3.14.2-slim-trixie

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD ["python3", "/app/solve.py"]
