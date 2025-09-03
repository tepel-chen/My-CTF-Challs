# 64jail

## 問題文

based jail

## Writeup

ASCII英字のみでコードを書こうとすると制約が強すぎる。そこで、Pythonの識別子がNFKCで Unicode正規化されることを利用する。以下の条件を満たすUnicode文字があると望ましい。
* UTF-8で、3バイトで表される(Base64は3バイト単位でエンコードされるため)
* Base64でエンコードしたときに小文字が含まれない
* NFKCでUnicode正規化すると小文字の英字となる

以下はそのような文字があるかを探索するコードである。

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

実行結果

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

見ての通り、a-yの範囲であればそのような文字が存在することがわかる。

次に、`(`と`)`を表現することを考える。`(`と`)`は前後に空白があっても良いため、空白やタブと組み合わせて3文字になる並びでエンコードしたときに小文字が含まれないパターンを探索する。

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

実行結果

```
['\t', '\x0c', ' ']
'( \t' KCAJ
'( \x0c' KCAM
') \t' KSAJ
') \x0c' KSAM
```

`( \t`と`) \t`がこの条件を満たすことがわかる。

a-yの英字と`(`と`)`がすべて表現できるようになったのであとは`exec(input())`と同等のコードを生成して実行すればよい。


## Flag

`fwectf{4pig4pii4pij4pig4pii4pij4pig4pii4pij}`

