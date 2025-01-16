FROM python:3.13.0-alpine3.20

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./run.sh

CMD ["sh", "run.sh"]