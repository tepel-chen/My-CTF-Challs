import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python disassembler.py <program_file>")
        sys.exit(1)
    program_file = sys.argv[1]
    with open(program_file, 'rb') as f:
        program = f.read()
    asm = ""
    for i in range(0, len(program), 3):
        opcode = program[i]
        oprand1 = program[i+1]
        oprand2 = program[i+2]
        if opcode == 0:
            asm += f"INP\tmem[{oprand1}]\n"
        elif opcode == 1:
            asm += f"MOV\tmem[{oprand1}]\t{oprand2}\n"
        elif opcode == 2:
            asm += f"MOV\tmem[{oprand1}]\tmem[{oprand2}]\n"
        elif opcode == 3:
            asm += f"ADD\tmem[{oprand1}]\tmem[{oprand2}]\n"
        elif opcode == 4:
            asm += f"MUL\tmem[{oprand1}]\tmem[{oprand2}]\n"
        elif opcode == 5:
            asm += f"XOR\tmem[{oprand1}]\tmem[{oprand2}]\n"
        elif opcode == 6:
            asm += f"NOT\tmem[{oprand1}]\n"
        else:
            print(f"Unknown opcode {opcode!r}")
            exit()
    with open("./program.asm", 'w') as f:
        f.write(asm)