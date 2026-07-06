# Lucky Redirect

[English](./README.md)

## 問題文

Google 検索の「検索」ボタンは一度も使ったことがありません。私には「I'm Feeling Lucky」ボタンだけで十分です。

### Beginner Hint

- 理論上はブラウザだけで解くことも可能ですが、solve script を使って解法を自動化することを強くおすすめします。

## Writeup

### 概要

```python
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("nope"))


for i in range(len(FLAG)):
    def make_route(i):
        @app.get("/" + "/".join(FLAG[:i+1]), endpoint=f"flag_{i}")
        def route():
            is_lucky = secrets.randbelow(5) == 0
            if is_lucky and i == len(FLAG) - 1:
                return f"Well done! The flag is: {FLAG}"
            elif is_lucky:
                return redirect(url_for(f"flag_{i+1}"))
            else:
                return redirect(url_for("nope"))

        return route

    make_route(i)


@app.get("/nope")
def nope():
    return "Nope"
```

`/A` にアクセスすると、20%の確率で `/A/l` にリダイレクトされ、80%の確率で `/nope` にリダイレクトされます。`/A/l` にアクセスした場合も、20%の確率で `/A/l/p` にリダイレクトされ、それ以外の場合は `/nope` にリダイレクトされます。このプロセスは、非常に運が良ければ、フラグが得られる `/A/l/p/a/c/a/{/[/ で区切られたフラグの内容]/}` にリダイレクトされるまで繰り返されます。

運だけで最後の文字までたどり着く確率は極めて低いです。どうにかして最後のルートまでたどり着くことはできないでしょうか？

### リダイレクトの仕組みを理解する

この問題を解くためには、まず HTTP におけるリダイレクトの仕組みを理解する必要があります。

サーバーがクライアントを別のページにリダイレクトさせるとき、以下のような HTTP レスポンスを返します。

```
HTTP/1.1 302 FOUND
Server: Werkzeug/3.1.8 Python/3.14.5
Date: Mon, 06 Jul 2026 03:48:24 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 197
Location: /nope
Connection: close

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/nope">/nope</a>. If not, click the link.
```

ここで留意すべき重要なポイントが2つあります。

* HTTP ステータスコードが `302` であり、これはクライアントに別のページへリダイレクトするよう指示するものです。
* `Location` ヘッザーは、リダイレクト先のターゲットルートを指定します。

リダイレクト先へ遷移するかどうかは、完全に HTTP クライアント側の責任であることに注意してください。この問題では、`/nope` へのリダイレクト指示に従うのではなく、サーバーがフラグの次の文字にリダイレクトしてくれるまでリクエストを再試行することができます。

### 再試行の自動化

フラグの長さは 42 文字です。各ステップの成功確率が 20% なので、フラグ全体を取得するには平均して 210 回（1文字あたり 5回）のリクエストを送信する必要があります。手動でこれを行うことも理論上は可能ですが、非常に面倒です。Python と [requests](https://pypi.org/project/requests/) ライブラリを使って自動化しましょう。

デフォルトでは、`requests` ライブラリは自動的にリダイレクトを追跡します。この挙動は、`allow_redirects` パラメータを `False` に設定することで無効化できます。

```python
response = requests.get(f"http://localhost:3000/A", allow_redirects=False)
```

`response.headers["Location"]` を確認することで、サーバーがどこにリダイレクトしようとしているかを知ることができます。もし `/nope` にリダイレクトされそうになったら現在のパスを再試行し、新しいサブパスにリダイレクトされたらその新しい URL に進みます。

サーバーがリダイレクトしなかった場合（つまり、`response.status_code` が `200` で `302` ではない場合）、最後のルートに無事到達したことを意味します。

最終的な solver スクリプトは以下のようになります。

```python
import requests
import os
URL = os.environ.get("URL", "http://localhost:3000/").rstrip("/")

known = "/A/l/p/a/c/a/%7B"

while True:
    response = requests.get(f"{URL}/" + known, allow_redirects=False)
    if response.status_code == 200:
        print(response.text)
        break
    if response.headers["Location"] != "/nope":
        known = response.headers["Location"]
```


## フラグ

`Alpaca{Ill_never_gamble_again_I_bet_on_it}`
