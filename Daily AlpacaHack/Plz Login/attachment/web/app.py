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
