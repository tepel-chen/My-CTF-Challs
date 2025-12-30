
# Useful Machine

## Description

This machine is very VERY useful!

Note: The flag format is `Alpaca{[\x20-\x7E]+}`.

## Writeup

### Overview

The program implements a simple virtual machine. Each opcode is represented by 1 byte, and is followed by 2 operands which are 1 byte each.

All operations are performed modulo 256, but it is omitted from the code.

|Opcode|Representation|Explanation|Code|
|---|---|---|---|
|0|`INP`|Read one byte from input and store it in memory.|`mem[operand1] = input`|
|1|`MOV`(immediate)|Move an immediate value into memory.|`mem[operand1] = operand2`|
|2|`MOV`(reference)|Copy a value from one memory cell to another.|`mem[operand1] = mem[operand2]`|
|3|`ADD`|Add two memory values and store the result in the destination.|`mem[operand1] = mem[operand1] + mem[operand2]`|
|4|`MUL`|Multiply two memory values and store the result in the destination.|`mem[operand1] = mem[operand1] * mem[operand2]`|
|5|`XOR`|Bitwise XOR two memory values and store the result in the destination.|`mem[operand1] = mem[operand1] ^ mem[operand2]`|
|6|`NOT`|Set destination to 1 if it is 0, otherwise set it to 0.|`mem[operand1] = 0 if mem[operand1] != 0 else 1`|

The goal of this challenge is to find an input that results in `mem[0] == 0`.

## Solution 1: Creating a Disassembler

The intended and probably one of the most versatile methods is to create a disassembler yourself. See [example implementation](./solution/disassembler.py). You will notice that the following code is repeated:

```
INP	mem[1]
ADD	mem[1]	mem[3]
MOV	mem[2]	<v1>
XOR	mem[1]	mem[2]
MOV	mem[3]	mem[1]
MOV	mem[2]	<v2>
ADD	mem[1]	mem[2]
NOT	mem[1]
MUL	mem[0]	mem[1]
```

Since the last instruction is `NOT mem[0]`, we want the `mem[0]` to be non-zero. This means that `mem[1]` must be 0 before `NOT mem[1]`. 

The pseudo-code will look like this:

```
val = (input + prev) % 256 # prev is initially 0
val = val ^ v1
prev = val
val = (val + v2) % 256 # Here val must be 0
```

In other words,

```
((v1 ^ (input + prev) % 256) + v2) % 256
```

must be 0. You can reverse the process to see that the input must match:

```
((256 - v2) ^ v1 - prev) % 256
```

Then, you can recover the whole flag. See [`solver1.py`](./solution/solver1.py) for the full solver.

## Solution 2: Dynamic Analysis

Instead of creating a full disassembler, you can print out some information while running the VM to understand how it works. You will find out that `mem[0]` will be non-zero for a longer time if you gave a correct input. Hence you can bruteforce each letter and see how many steps until `mem[0]` becomes 0.

See [`solver2.py`](./solution/solver2.py) for the full solver. 


## Flag

`Alpaca{Futures_Made_of_Virtual_Machines}` [video](https://youtu.be/4JkIs37a2JE)
