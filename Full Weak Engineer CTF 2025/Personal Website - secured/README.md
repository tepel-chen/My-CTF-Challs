# Personal Website

## Description

I heard my website isn't secure. I made it persistent by using a database so that I can recover it if something goes wrong.


## Writeup 

For explaination on class pollution and depth check bypass, see [Personal Website](/Full%20Weak%20Engineer%20CTF%202025/Personal%20Website).

shelve serializes and deserializes user objects [using pickle](https://github.com/python/cpython/blob/v3.13.6/Lib/shelve.py#L114).
Since pickle is powerful enough to allow RCE depending on how it is used, the next step is to investigate whether a class pollution gadget exists here.

### Failed Approach 1: Modifying Opcodes

Looking at [pickle.py](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py), we can see that many global variables are defined. At first glance, it might seem possible to achieve RCE by altering some of them. For example, one might try changing the opcode characters so that serialization and deserialization interpret them differently, potentially leading to code execution.

Unfortunately, this approach does not work. The implementation in `pickle.py` is only a fallback; in most cases, the actual implementation is in [pickle.c (C code)](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1819). Since opcodes in the C implementation are hard-coded, they cannot be modified through Class Pollution.

### Failed Approach 2: Changing ` __qualname__`

If we look at the [implementation of `save_global`](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1072), we can see that pickle refers to an object’s class using both `obj.__module__` and `obj.__qualname__`.
Thus, one might think of setting:

```python
obj.__module__ = 'subprocess'
obj.__qualname__ = 'Popen'
```

so that the deserialized class becomes `subprocess.Popen`.

However, this also fails. When serializing, pickle verifies that the class obtained by importing `__module__` and `__qualname__` matches the actual class of the object being serialized. If they do not match, an error is raised.

### Step 1: Exploiting `fix_imports`

Pickle has protocol versions ranging from 0 to 5. Protocols up to version 2 were designed for Python 2 compatibility. For protocols ≤2, [special handling](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1150) is included to fix differences between Python 2 and 3 imports. Importantly, this fix is applied after the identity check mentioned in Failed Approach 2. This suggests that, if successful, we could alter which class gets deserialized.

This process uses global variables in the `_compat_pickle` module. Since these are also [imported and used in _pickle.c](https://github.com/python/cpython/blob/v3.13.6/Modules/_pickle.c#L344), they can be modified through class pollution.

Furthermore, in shelve, the protocol version is determined by referencing `DEFAULT_PROTOCOL` [at each instantiation](https://github.com/python/cpython/blob/v3.13.6/Lib/shelve.py#L88). Thus, the protocol version can also be changed using class pollution.

For example:

```python
_compat_pickle.REVERSE_NAME_MAPPING[("user", "User")] = ("subprocess", "Popen")
```

would cause deserialization as `subprocess.Popen`. However, since the dictionary keys are tuples, this cannot be modified through class pollution in this challenge.

Instead, we can try:

```python
_compat_pickle.REVERSE_IMPORT_MAPPING["user"] = "subprocess"
```

which makes pickle attempt to import `subprocess.User`. But since there is no `User` class in the subprocess module, or any other module (aside from user.User), and importing new classes is blocked by audit hooks, this alone does not achieve RCE.

### Step 2: Newline Injection

The way classes are serialized differs between protocol versions ≤2 and ≥3. In protocol version 2, serialization looks like this ([source](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1158)):

```python
    self.write(GLOBAL + bytes(module_name, "ascii") + b'\n' +
                bytes(name, "ascii") + b'\n')
```
And deserialization is handled as ([source](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1569)):

```python
    def load_global(self):
        module = self.readline()[:-1].decode("utf-8")
        name = self.readline()[:-1].decode("utf-8")
        klass = self.find_class(module, name)
        self.append(klass)
    dispatch[GLOBAL[0]] = load_global
```

Here, `module_name` is not checked for newline characters in serialization. If a newline is included, the part before the newline is treated as the module name, and the part after is treated as the class name. The remaining data is interpreted as additional opcodes/operands, which means we can effectively inject arbitrary pickle instructions.

## Flag

`fwectf{placeholder_<dynamic>}`



