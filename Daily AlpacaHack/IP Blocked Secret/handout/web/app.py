import os
from flask import Flask, g, redirect, request, url_for, session, render_template_string
import re
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    print("SECRET_KEY is not set")
    exit()


IPV4_RE = re.compile(r"\d{,3}.\d{,3}.\d{,3}.\d{,3}", re.ASCII)

@app.before_request
def set_db():
    g.db = sqlite3.connect("/tmp/app.db")
    g.db.row_factory = sqlite3.Row


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()

INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>IP Blocked Secret</title>
</head>
<body>
    Your current secret: {{ secret }}
    <h2>Update secret</h2>
    <form action="/set" method="POST">
        <input name="secret" placeholder="My password is Passw0rd">
        <input type="submit">
    </form>
</body>
</html>
""".strip()

@app.get("/")
def index():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    sid = session.get("sid", None)
    if not IPV4_RE.fullmatch(ip):
        return "Invalid IP", 400
        
    data = g.db.execute(f"""
        SELECT secret, ip FROM secrets WHERE id='{sid}'
    """).fetchone()
    if not data:
        return render_template_string(INDEX, secret="No secret yet")
    
    if ip != data["ip"]:
        return "Unauthorized", 403
    
    return render_template_string(INDEX, secret=data["secret"])


@app.post("/set")
def set():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    secret = request.form.get("secret", "")
    if not IPV4_RE.fullmatch(ip):
        return "Invalid IP", 400
    
    secret = secret.replace("'", "''")
    cur = g.db.execute(f"""
        INSERT INTO secrets (ip, secret)
        VALUES ('{ip}', '{secret}')
        ON CONFLICT(ip) DO UPDATE SET
            secret = excluded.secret
        RETURNING id
    """)
    session["sid"] = cur.fetchone()["id"]
    g.db.commit()
    return redirect(url_for("index"))
