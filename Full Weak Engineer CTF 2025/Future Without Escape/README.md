# Future Without Escape

## Description

There will be no exit

## Author

t-chen, ryhtbsh

## Wrteup 

We use [this UAF](https://github.com/python/cpython/issues/126405).

When the UAF occurs, creating a 15-byte bytes object causes those bytes to be written into the freed memory region. At that location, the following PyObject structure is expected ([reference](https://github.com/python/cpython/blob/c22cc8fccdd299fa923f04e253a3f7c59ce88bfe/Include/object.h#L125)):

```c
typedef struct _object {  
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
} PyObject;
```

After the UAF is triggered, [`do_richcompare`](https://github.com/python/cpython/blob/ab2a3dda1d3b6668162a847bf5b6aca2855a3416/Objects/object.c#L1044) executes `Py_TYPE(w)->tp_richcompare`. Conveniently, at this point the first argument (rdi) is the object itself. By forging a `PyObject` and `PyTypeObject` such that `tp_richcompare` points to `plt.system` and rdi points to the string `/bin/sh\0`, `system("/bin/sh")` will be invoked, resulting in RCE.

Since this Python build is PIE-enabled, the address of `plt.system` cannot be known statically. However, small integer objects are allocated in the [`.data` section](https://github.com/python/cpython/blob/3cfab449ab1e3c1472d2a33dc3fae3dc06c39f7b/Include/internal/pycore_runtime_structs.h#L121) at startup, so the value of `id(1)` reveals a fixed location in `.data`. This allows calculation of the base address of libpython, from which the address of `plt.system` can then be derived.

## Special thanks

Special thanks to oh_word for playtesting this challenge, and for verifying that there was no non-pwn solution. Additionally, he was the one who originally opened the GitHub issue for the UAF bug.

## Flag

`fwectf{7h3_fu7ur3_574r75_70d4y_n07_70m0rr0w}`

