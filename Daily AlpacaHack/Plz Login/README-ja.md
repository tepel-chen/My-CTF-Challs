# Plz Login

[English](./README.md)

## 説明

ログインして！パスワードは教えないよ！

## Writeup

### 概要

目的はシンプルで、パスワードを推測してこのサーバにログインすることです。

```python
from flask import Flask, request, render_template
import os
import random 

FLAG = os.environ.get("FLAG", "Alpaca{**REDACTED**}")

app = Flask(__name__)
app.secret_key = random.randbytes(32).hex()

@app.get("/")
def index():

    return render_template("login.html")

@app.post("/login")
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username[0] not in "aA" or username[1:] != "dmin" or password != "**REDACTED**":
        return render_template("login.html", error="You are not Admin"), 401

    return render_template("flag.html", flag=FLAG)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
```

### 解法

本質的な脆弱性は、このサーバが `debug=True` で動作している点です。これは本番運用では安全でないデバッグ機能を有効にします。

その一つが、エラー発生時にトレースバックを表示する機能です。パスワードがある行の近くでエラーを起こせば、その行がレスポンスに表示されます。

ここでは、`username` が空文字のとき `username[0]` が `IndexError` を起こします。これは`curl` や Python を利用することで実行できます（`solver.py` を参照）。または、ブラウザで HTML を編集し、`minlength="5"` を削除して空のユーザ名で送信しても可能です。

![alt text](image.png)

漏れたパスワードを使ってフラグを取得しましょう！

### フラグ

```
Alpaca{fulasukuuuuuuuuu_in_d3bug_m0de}
```
