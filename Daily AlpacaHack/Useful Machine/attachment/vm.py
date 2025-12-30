
import sys

class VM:
    def __init__(self, program: bytes):
        self.program = program
        self.mem = [0] * 256
        self.ip = 0

    def _read_input_char(self) -> str:
        ch = sys.stdin.read(1)
        if ch == "":
            return "\x00"
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

    def run(self, max_steps: int = 10_000_000) -> bool:
        steps = 0
        while steps < max_steps and self.step():
            steps += 1
        return self.mem[0] == 0

if __name__ == "__main__":

    with open("program", "rb") as f:
        program = f.read()

    vm = VM(program)
    print("Input flag: ")
    if vm.run():
        print("Correct flag!")
    else:
        print("Incorrect flag.")