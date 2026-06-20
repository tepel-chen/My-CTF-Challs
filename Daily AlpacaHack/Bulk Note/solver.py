import requests
import os

URL = os.getenv("URL", "http://localhost:3000/")

s = requests.session()

r = s.post(URL, data="""
- &anchor
  command: create
  content: foobar
  isHidden: true
- *anchor
""", headers={
    "Content-Type": "application/yaml"
})

note_id = r.json()["results"][0]["id"]

r = s.post(URL, data=f"""
- command: get
  id: {note_id}
""", headers={
    "Content-Type": "application/yaml"
})

print(r.json()["results"][0]["content"])
    
