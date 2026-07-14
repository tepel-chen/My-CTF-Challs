#!/bin/sh
set -eu

python /app/init_db.py

export SECRET_KEY="$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')"
exec gunicorn -b 0.0.0.0:3000 app:app --workers 4 --threads 2