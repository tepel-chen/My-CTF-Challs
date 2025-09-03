from pwn import *
import string
import time

context.log_level='warn'

REMOTE = True


def create_pattern():
    pattern = list(range(100))
    pattern[0], pattern[48] = pattern[48], pattern[0] 
    pattern[3], pattern[49] = pattern[49], pattern[3] 
    for i in range(15):
        pattern[2*i+5], pattern[i+51] = pattern[i+51], pattern[2*i+5]
    return pattern

def test(io, s, pattern):
    prefix = s + ("." * (33-len(s)))
    for i in range(100):
        io.sendlineafter(f"element {i}> ".encode(), prefix.encode() + bytes([pattern[i] + 0x11]))
    start = time.time()
    io.recvline_contains(b"first")
    res = time.time() - start
    print(s, res)
    return res

io = remote("chal1.fwectf.com", 8015) if REMOTE else process(["python", "quick.py"])

pattern = create_pattern()
pattern_a_time = test(io, "fx", pattern)
pattern_b_time = test(io, "fv", pattern)
threshold = (pattern_a_time + pattern_b_time) / 2
print(f"{pattern_a_time=}")
print(f"{pattern_b_time=}")
print(f"{threshold=}")


known = "fwectf{"
chars = list(reversed(string.digits +  "_" + string.ascii_lowercase))
while len(known) < 33:
    lo, hi = 0, len(chars) - 1
    best = chars[0]
    while lo <= hi:
        mid = (lo + hi) // 2
        c = chars[mid]
        current = known + c
        if test(io, current, pattern) > threshold:
            best = c
            hi = mid - 1
        else:
            lo = mid + 1
    known += best
    print(f"current: {known}")
print(known + "}")