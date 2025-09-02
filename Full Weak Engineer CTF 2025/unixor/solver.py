"""
nihon.txtは同じくChatGPTで生成した小説
"""
sample_text = open("nihon.txt", "rb").read()
d = {}
for c in sample_text:
    if c not in d:
        d[c] = 0
    d[c] += 1


encrypted = open("encrypted.txt", "rb").read()
len_score = []
for i in range(22):
    score = 0
    for j, c in enumerate(b"fwectf{"):
        score += sum([d.get(c ^ e, 0) for e in encrypted[j::i+8]])
    len_score.append(score/(len(encrypted)//(i+8)))

l = len_score.index(max(len_score))
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

print(bytes([a ^ ord(FLAG[i % len(FLAG)]) for i, a in enumerate(encrypted)]).decode('utf-8'))