# docker run -it -e URL=http://localhost:3000/ --network=host $(docker build -q ./solution)
import os
import requests

URL = os.getenv("URL", f"http://localhost:3000/") 


response = requests.post(f"{URL}login", data={
    "username": "constructor"
})
print(response.text)

