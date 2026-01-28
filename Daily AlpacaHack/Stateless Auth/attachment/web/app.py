from flask import Flask, request, render_template, redirect, url_for, make_response
import jwt
import time
import random
import os
import os.path

app = Flask(__name__)

if not os.path.exists("static/jwt_secret.txt"):
    JWT_SECRET = random.randbytes(32).hex()
    with open("static/jwt_secret.txt", "w") as f:
        f.write(JWT_SECRET)
else:
    with open("static/jwt_secret.txt") as f:
        JWT_SECRET = f.read()

JWT_EXP = 60 * 60
FLAG = os.environ.get("FLAG", "Alpaca{REDACTED}")


def issue_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


@app.get("/")
def index():
    return render_template("login.html")


@app.post("/login")
def login():
    username = request.form.get("username", "")

    if not username:
        return render_template("login.html", error="username required")

    if username.lower() == "admin":
        return render_template("login.html", error="admin is forbidden")

    token = issue_token(username)

    resp = make_response(redirect(url_for("dashboard")))
    resp.set_cookie(
        "token",
        token,
        httponly=True,
    )
    return resp


@app.get("/dashboard")
def dashboard():
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("index"))

    try:
        payload = verify_token(token)
    except:
        return redirect(url_for("index"))

    return render_template(
        "dashboard.html",
        username=payload["sub"],
        flag=FLAG if payload["sub"] == "admin" else "No flag for you!"
    )


@app.get("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("token")
    return resp
