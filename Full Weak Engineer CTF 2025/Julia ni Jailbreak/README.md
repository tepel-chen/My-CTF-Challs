# Julia ni Jailbreak

## Description

https://youtu.be/vdPIPVsx0B0

## Writeup

We exploit [this bug](https://github.com/JuliaLang/julia/issues/54328). When constructing multi-dimensional arrays, an integer overflow allows the check for whether the array can be laid out in memory can be bypassed, enabling the creation of an array that can access the entire memory space. Using this, AAR/AAW becomes possible.

There are several follow-up approaches (e.g., ROP), but the simplest is to overwrite the stack-resident flag that controls whether to drop into the [REPL after the script finishes](https://github.com/JuliaLang/julia/blob/99663f5828517f31f7b50ab17ca1e2d59ae4f2e3/base/client.jl#L241), thereby launching the REPL.

Here's the detailed steps:

* Since PIE is disabled, leak the libc base address from a pointer into libc that is stored in Julia’s `.data`.
* From a pointer into ld.so that is stored in libc’s `.data`, leak the ld.so base address.
* From the address of environ in ld.so, leak a stack address.
* Overwrite the "enter REPL" flag on the stack to transition into the REPL.
* Retrieve the flag with ``run(`cat flag.txt`)``
    * Using ``run(`/bin/sh`)`` is not possible here because it would exceed the maximum allowed number of processes (5).
    
## Flag

`fwectf{Kaerouze_ano_machikado_he_Jailbreak_ol_my_my_my_my_Julia!!!!!!!}`

