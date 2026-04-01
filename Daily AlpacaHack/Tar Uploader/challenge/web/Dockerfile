FROM python:3.13.12-slim-trixie

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY templates templates
COPY app.py app.py
COPY flag.txt /flag.txt

# Make sure that any directory outside /app/static isn't writeable
RUN mkdir static
RUN chmod a+w static
USER nobody

CMD python app.py
