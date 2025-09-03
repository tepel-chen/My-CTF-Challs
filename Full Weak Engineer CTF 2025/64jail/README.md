# 64jail

## Description

based jail

## Writeup

When writing code using only ASCII letters, the constraints are too strict. To work around this, we can take advantage of the fact that Python identifiers are normalized with Unicode NFKC. It is convenient if we can find Unicode characters that satisfy the following conditions:
* They are represented as 3 bytes in UTF-8 (since Base64 encodes in 3-byte units).
* Their Base64 encoding contains no lowercase letters.
* When normalized with NFKC, they become lowercase English letters.

The following code searches for such characters:

```python
from base64 import b64encode
import string

for ch in string.ascii_lowercase:
    exec(f"{ch} = 'foobar'")
allowed = string.ascii_uppercase + string.digits

for ind in range(0x110000):
    try:
        enc = b64encode(chr(ind).encode()).decode()
        assert all(ec in allowed for ec in enc)
        assert eval(chr(ind)) == "foobar"
        print(ind, chr(ind), enc)
    except:
        pass
```
Execution result:
```
65345 ａ 772B
65346 ｂ 772C
65347 ｃ 772D
65348 ｄ 772E
65349 ｅ 772F
65350 ｆ 772G
65351 ｇ 772H
65352 ｈ 772I
65353 ｉ 772J
65354 ｊ 772K
65355 ｋ 772L
65356 ｌ 772M
65357 ｍ 772N
65358 ｎ 772O
65359 ｏ 772P
65360 ｐ 772Q
65361 ｑ 772R
65362 ｒ 772S
65363 ｓ 772T
65364 ｔ 772U
65365 ｕ 772V
65366 ｖ 772W
65367 ｗ 772X
65368 ｘ 772Y
65369 ｙ 772Z
```

As you can see, such characters exist for the range from a to y.

Next, let’s consider representing `(` and `)`. Since spaces before and after them are allowed, we search for 3-character combinations of space or tab characters together with `(` or `)` whose Base64 encoding contains no lowercase letters.

```python
from base64 import b64encode
import string
import itertools

allowed = string.ascii_uppercase + string.digits

def a():
    return 'foobar'

spaces = []
for i in range(0x7f):
    try:
        if eval(f"a{chr(i)}()") == 'foobar':
            spaces.append(chr(i))
    except:
        pass
print(spaces) # ['\t', '\x0c', ' ']

for r in itertools.permutations(spaces + ['('], 3):
    if '(' not in r:
        continue
    s =''.join(r)
    enc = b64encode(s.encode()).decode()
    if all(ec in allowed for ec in enc):
        print(repr(s), enc)


for r in itertools.permutations(spaces + [')'], 3):
    if ')' not in r:
        continue
    s =''.join(r)
    enc = b64encode(s.encode()).decode()
    if all(ec in allowed for ec in enc):
        print(repr(s), enc)
```

Execution result:

```
['\t', '\x0c', ' ']
'( \t' KCAJ
'( \x0c' KCAM
') \t' KSAJ
') \x0c' KSAM
```

We can see that `( \t` and `) \t` satisfy the condition.

Now that we can represent the letters a through y as well as `(` and `)`, we can generate code equivalent to `exec(input())` and execute it.

## Flag

`fwectf{4pig4pii4pij4pig4pii4pij4pig4pii4pij}`

