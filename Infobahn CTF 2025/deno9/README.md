# deno9

## Description

Another day passes by,

Just like every day I spend with you.

## Writeup

You can run 
```bash
sqlite3 v8_code_cache_v2 "SELECT hex(data) FROM codecache" | xxd -r -p > ./cache_orig.bin
```
to extract the v8 cache. Also, you can run:
```bash
deno run --v8-flags=--print-bytecode main.ts
```
to run the script and output bytecode. From there, you can deduce the meaning of opcodes and the meaning of operands. 

Create a disassembler and recover the true numbers.

See `solve.py` for the full script.