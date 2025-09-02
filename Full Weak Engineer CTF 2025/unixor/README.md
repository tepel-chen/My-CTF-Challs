# unixor

## Description

I wanna be a novelist

## Writeup

This is an XOR cipher, where each byte of the plaintext corresponds one-to-one with a byte of the ciphertext. Therefore, decryption is possible using frequency analysis.

First, in the same way, we generate a novel file `nihon.txt` with ChatGPT. Based on this file, we create a dictionary that records how many times each byte appears:

```python
sample_text = open("nihon.txt", "rb").read()
d = {}
for c in sample_text:
    if c not in d:
        d[c] = 0
    d[c] += 1
```

Next, we take advantage of the fact that the flag follows the format `fwectf{...}` to determine its length.
Once we assume the flag length, the positions that are XORed with `fwectf{` are fixed. We can then XOR those positions and compare the results against the frequency dictionary above, calculating a "score" that measures how similar the frequencies are.

```python
encrypted = open("encrypted.txt", "rb").read()
for i in range(22):
    score = 0
    for j, c in enumerate(b"fwectf{"):
        score += sum([d.get(c ^ e, 0) for e in encrypted[j::i+8]])
```

We then use the length that gives the maximum score to recover the rest of the flag. For each character position in the flag, we test candidate characters one by one, compute the score in the same way, and choose the character with the highest score.

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

Finally, we verify that the ciphertext is correctly decrypted. In my experiments, this method has not failed; but even if it does fail by chance, you can regenerate `nihon.txt` or manually test suspicious positions one by one to correct the result.


## Flag

`fwectf{dC0D3_fR_1S_D34d}`

