# unixor

## 問題文

I wanna be a novelist

## Writeup

これはXOR暗号であり、平文のときの1バイトと暗号のときの1バイトが1対1対応する。したがって、頻度分析による復号が可能である。

まず、同じようにChatGPTを利用して小説`nihon.txt`を作成する。そして、これを元にあるバイトが何度出現したかの辞書を作成する。

```python
sample_text = open("nihon.txt", "rb").read()
d = {}
for c in sample_text:
    if c not in d:
        d[c] = 0
    d[c] += 1
```

次に、フラグが`fwectf{...}`の形式で表されることを利用して、フラグの長さを求める。
フラグの長さを仮定すると、`fwectf{`に対応するXORされる箇所が確定するので、その箇所をXORした結果と前述の辞書を比較して、どれくらい頻度が似通っているかのスコアを計算する。
```python
encrypted = open("encrypted.txt", "rb").read()
for i in range(22):
    score = 0
    for j, c in enumerate(b"fwectf{"):
        score += sum([d.get(c ^ e, 0) for e in encrypted[j::i+8]])
```

スコアが最大のものを利用して残りのフラグを求める。フフラグの各文字位置について、1文字ずつ試して上記と同様にスコアを求め、最大のものを選択する

```python
flg = ""
for i in range(l):
    max_score = -1
    max_c = ""
    for c in b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!?":
        score = sum([d.get(c ^ e, 0) for e in encrypted[i+7::l+8]])
        if score > max_score:
            max_score = score
            max_c = c
    flg += chr(max_c)

FLAG = "fwectf{" + flg + "}"
print(FLAG)
```

最後に、実際に暗号が復号されているかを確認する。私が試した限りでは、この方法で失敗したケースはなかったが、運悪く失敗したとしてもnihon.txtを再生成してみるなり、合わなさそうな箇所を一つずつ試したりすることで修正できるだろう。


## Flag

`fwectf{dC0D3_fR_1S_D34d}`

