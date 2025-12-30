import sys


import sys

class VM:
    def __init__(self, program: bytes, input: str):
        self.program = program
        self.mem = [0] * 256
        self.ip = 0
        self.input = input
        self.input_count = 0
    
    def _read_input_char(self) -> str:
        ch = self.input[self.input_count]
        self.input_count += 1
        return ch

    def step(self) -> bool:
        if self.ip < 0 or self.ip >= len(self.program):
            return False

        code = self.program
        opcode = code[self.ip]
        oprand1 = code[self.ip + 1]
        oprand2 = code[self.ip + 2]
        self.ip += 3
        if opcode == 0:
            ch = self._read_input_char()
            self.mem[oprand1] = ord(ch) % 256
        elif opcode == 1:
            self.mem[oprand1] = oprand2
        elif opcode == 2:
            self.mem[oprand1] = self.mem[oprand2]
        elif opcode == 3:
            self.mem[oprand1] = (self.mem[oprand1] + self.mem[oprand2]) % 256
        elif opcode == 4:
            self.mem[oprand1] = (self.mem[oprand1] * self.mem[oprand2]) % 256
        elif opcode == 5:
            self.mem[oprand1] = self.mem[oprand1] ^ self.mem[oprand2]
        elif opcode == 6:
            self.mem[oprand1] = 0 if self.mem[oprand1] != 0 else 1
        else:
            raise RuntimeError(f"Unknown opcode {opcode!r} at ip={self.ip}")
        return True

    def run(self, max_steps: int = 10_000_000) -> int:
        steps = 0
        while steps < max_steps and self.step():
            steps += 1
            if steps > 0 and self.mem[0] == 0:
                return steps
        return -1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python solver2.py <program_file>")
        sys.exit(1)
    program_file = sys.argv[1]
    with open(program_file, 'rb') as f:
        program = f.read()
    known = "Alpaca{"
    chars = [chr(i) for i in range(0x20, 0x7f)]
    while known[-1] != "}":
        max_steps = 0
        max_val = None
        for c in chars:
            current = known + c + ("." * 100) # add padding
            vm = VM(program, current)
            result = vm.run()
            if max_steps < result:
                max_steps = result
                max_val = c
        known += max_val
        print("Current value: ", known)
    print("Recovered flag:", known)
