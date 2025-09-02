# reeeeeee

## 問題文

^re{7}$

## Writeup


`_sre.compile`は`int`の配列から正規表現の中間表現をコンパイルする非標準の関数のため、まともなドキュメンテーションがない。したがって、その使い方を知るためにはソースコードを見に行く必要がある。利用されている箇所は[ここ](https://github.com/python/cpython/blob/5c6937ad204d009085e016c3dc9e9ba75eef34c5/Lib/re/_compiler.py#L757)であるが、よく見るとその上に、デバッグ用に`re._compiler.dis`を呼ぶコードがある。これを利用するとディスアセンブルすることができるので、何をやっているか少しわかるようになる。

```python
arr = [14, 4, 0,...]

from re._compiler import dis

dis(arr)
```

まず以下の箇所について
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
* (8): 行の始まり(正規表現でいうと`^`)
* (10,12,14,16,18,22): "fwectf{"と続き
* (24~40): 以下を48回繰り返す
    * `[0x00000000, 0x83ff0002, 0x87fffffe, 0x07fffffe, 0x00000000, 0x00000000, 0x00000000, 0x00000000]` は0〜255のコードポイントに対するビットマップで、どのバイトが許可されるかを示す。ここでは、`a-zA-Z0-9!?_`である
    * 上記の文字でなければマッチ失敗
* (41): "}"が続く
* (43): 行の終わり(正規表現でいうと`$`)

したがって、これは`^fwectf\{[a-zA-Z0-9!?_]{48}\}$`を表している。また5行目のASSERTは`(?=...)`に対応するので、続く正規表現を先読みしている。

次のブロックは

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

* (49)行の始まり
* (51)以下を可能な限り繰り返す(正規表現の`*`)
    * (55, 61)以下のいずれかを満たす
        * (55) パターン1 - (57)"c"から始まらない
        * (61) パターン2
            * (62) "c"から始まる
            * (64)以下を先読み
                * (69) 以下のどちらかを満たす
                    * (71) "t"が続く
                    * (73) "0"が続く

したがって、これは`(?=^([^c]|c(?=(t|0)))*$)`であり、「文字列中に`c`が出現した場合、`t`か`0`が続く、と言い換えることができる。

残りのブロックも同様のパターンであるので、それをうまく条件に落とし込み、ソルバーを作成する。再帰関数を用いる方法なども考えられるが、[ここ](./solver)ではz3を用いた方法を用いた。


## Flag

`fwectf{c0Mp1l3d_R39eXxX!_wh1?h_D1sS4Ss3mB!Er_d1D_U_us3?}`

