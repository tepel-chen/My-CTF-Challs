import re
from flask import Flask, request, Response

app = Flask(__name__)

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
