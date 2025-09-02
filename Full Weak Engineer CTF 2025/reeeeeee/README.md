# reeeeeee

## Description

^re{7}$

## Writeup

`_sre.compile` is a non-standard function that compiles an intermediate representation of a regular expression from an array of integers, so there is no proper documentation available. Therefore, to understand how it works, you need to look at the source code. It is used [here](https://github.com/python/cpython/blob/5c6937ad204d009085e016c3dc9e9ba75eef34c5/Lib/re/_compiler.py#L757), and just above that, there is code that calls `re._compiler.dis` for debugging purposes. By using this, you can disassemble the intermediate representation and get a better idea of what is happening.


```python
arr = [14, 4, 0,...]

from re._compiler import dis

dis(arr)
```

For example, consider the following part:

```
   5: ASSERT 40 0 (to 46)
   8.   AT BEGINNING
  10.   LITERAL 0x66 ('f')
  12.   LITERAL 0x77 ('w')
  14.   LITERAL 0x65 ('e')
  16.   LITERAL 0x63 ('c')
  18.   LITERAL 0x74 ('t')
  20.   LITERAL 0x66 ('f')
  22.   LITERAL 0x7b ('{')
  24.   REPEAT_ONE 16 48 48 (to 41)
  28.     IN 11 (to 40)
  30.       CHARSET [0x00000000, 0x83ff0002, 0x87fffffe, 0x07fffffe, 0x00000000, 0x00000000, 0x00000000, 0x00000000]
  39.       FAILURE
  40:     SUCCESS
  41:   LITERAL 0x7d ('}')
  43.   AT END
  45.   SUCCESS
```

* (8): Beginning of string (^)
* (10,12,14,16,18,20,22): Matches "fwectf{"
* (24–40): Repeats the following 48 times
    * The array [0x00000000, 0x83ff0002, 0x87fffffe, 0x07fffffe, 0x00000000, 0x00000000, 0x00000000, 0x00000000] is a bitmap for code points 0–255, showing which bytes are allowed. Here it corresponds to a-zA-Z0-9!?_.
    * If the character is not in the allowed set, the match fails.
* (41): Matches "}"
* (43): End of string ($)

Therefore, this represents the regular expression `^fwectf\{[a-zA-Z0-9!?_]{48}\}$`. Also, the ASSERT at line 5 corresponds to a lookahead `(?=...)`.

The next block is:


```
  46: ASSERT 39 0 (to 86)
  49.   AT BEGINNING
  51.   REPEAT 30 0 MAXREPEAT (to 82)
  55.     BRANCH 5 (to 61)
  57.       NOT_LITERAL 0x63 ('c')
  59.       JUMP 22 (to 82)
  61:     branch 20 (to 81)
  62.       LITERAL 0x63 ('c')
  64.       ASSERT 14 0 (to 79)
  67.         MARK 0
  69.         IN 6 (to 76)
  71.           LITERAL 0x74 ('t')
  73.           LITERAL 0x30 ('0')
  75.           FAILURE
  76:         MARK 1
  78.         SUCCESS
  79:       JUMP 2 (to 82)
  81:     FAILURE
  82:   MAX_UNTIL
  83.   AT END
  85.   SUCCESS
```

* (49): Beginning of string
* (51–82): Repeat as many times as possible (*)
    * (57) Branch 1: Does not start with "c"
    * (62) Branch 2: Start with "c", then
        * (64): Lookahead the following:
            * (69): Either:
                * (71): "t" follows
                * (73): "0" follows

Thus, this corresponds to: `(?=^([^c]|c(?=(t|0)))*$)`. In other words: "Whenever `c` appears in the string, it must be followed by either `t` or `0`."

The remaining blocks follow a similar pattern. By reducing them to conditions like this, you can build a solver. While it’s possible to write a recursive function to handle this, in the solver [here](./solver) a Z3-based approach was used instead.

## Flag

`fwectf{c0Mp1l3d_R39eXxX!_wh1?h_D1sS4Ss3mB!Er_d1D_U_us3?}`

