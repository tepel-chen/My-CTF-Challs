import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python solver1.py <disassembled_file>")
        sys.exit(1)
    
    disassembled_file = sys.argv[1]
    with open(disassembled_file, 'r') as f:
        asm = f.read()
    lines = asm.strip().split('\n')
    prev = 0
    ans = ""
    for i in range(40):
        v1 = int(lines[i * 9 + 3].split()[2])
        v2 = int(lines[i * 9 + 6].split()[2])
        ans += chr((((256 - v2) ^ v1) - prev) % 256)
        prev = 256 - v2
    print("Recovered flag:", ans)
