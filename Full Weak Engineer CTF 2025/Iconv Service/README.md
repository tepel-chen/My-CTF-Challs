# Iconv Service

## Description

"Chaining iconv filters in pwn… but not in PHP?” - anonymous web CTF player

## Writeup

The vulnerability lies in the following section:

```c
    int src, dst;
    char from[32], to[32];
    printf("Source index (0-2) > ");
    scanf("%d", &src);
    printf("Destination index (0-2) > ");
    scanf("%d", &dst);
    printf("From encoding > ");
    scanf("%31s", from);
    printf("To encoding > ");
    scanf("%31s", to);
```

Since there is no validation for the `src` and `dst` indices, it is possible to convert data from out-of-bounds regions or write data beyond valid ranges. However, the input and output commands do enforce index checks, meaning that in order to output out-of-bounds data, it must first be copied into a valid buffer.

That said, attempting to copy from `buf[3]` to `buf[0]` will result in an error because the value of `buf[3].left` is too large:

```
1: input | 2: output | 3: convert | 4: exit
> 3
Source index (0-2) > 3
Destination index (0-2) > 0
From encoding > LATIN1
To encoding > LATIN1
iconv: Argument list too long
```

To bypass this, we exploit another implementation flaw:

```c
    char *outptr = bufs[dst].buf;
    bufs[dst].left = BUFF_SIZE;

    size_t res = iconv(cd, &inptr, &(bufs[src].left), &outptr, &(bufs[dst].left));
    if (res == (size_t)-1) {
        perror("iconv");
    } else {
        bufs[dst].left = BUFF_SIZE - bufs[dst].left;
    }
```

Here, `bufs[dst].left` is initialized to `BUFF_SIZE`, but if iconv fails, it is not reset and remains unchanged. Therefore, if conversion fails on the very first byte, `bufs[dst].left` remains at `BUFF_SIZE`. To trigger this behavior, one can set the encoding to UTF-8 and provide an invalid byte sequence in `bufs[src].buf`.

Furthermore, by using an encoding like `LATIN1`, which never fails regardless of the byte value, out-of-bounds memory can be copied directly into a valid buffer.

By leveraging these issues, arbitrary code execution can be achieved through the following steps:

* Correct the value of `bufs[3].left`.
* Copy `bufs[3].buf` into `bufs[0].buf` using LATIN1.
* Since `bufs[3].buf` contains the stack canary, fill all bytes up to the canary with non-null values. Then, when printing `bufs[0].buf`, the canary leaks.
* Similarly, since `bufs[3].buf` also contains addresses from libc, these can also be leaked.
* Write a ROP payload and the correct stack canary into `bufs[0].buf`, then copy it back into `bufs[3].buf`.
* Finally, execute ROP and gain RCE.

## Flag

`fwectf{C0nv_75uyu_h4_y4m454}`

