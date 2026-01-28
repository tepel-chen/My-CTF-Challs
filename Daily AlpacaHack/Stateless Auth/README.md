
# Stateless Auth

[日本語はこちら](./README-ja.md)

## Description

Why do you need a database?

## Writeup

### Overview

When you submit your username to the `/login` endpoint, you are issued a **JWT (JSON Web Token)** containing the name you entered. However, you cannot use `admin` as a username.

```python
def issue_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
# ... 
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
```

When you visit `/dashboard` with the username `admin`, you receive the flag.

```python
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
```

### Understanding JWT

So what is a JWT? When you inspect the token stored in your cookie, it looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiaWF0IjoxNzY5NjEwODg1LCJleHAiOjE3Njk2MTQ0ODV9.oy4uCRSwvCnq4q7sUpFrNLsJFGlP2tghj38JRFVpcx0
```

As you can see, the token consists of 3 parts separated by `.`. These parts are encoded with Base64. To visualize each part, I recommend using [jwt.io](https://www.jwt.io/)

![alt text](image-1.png)

The second part is the payload. You can see JSON containing `sub`, `iat`, and `exp`. `sub` represents the username, and the token is only valid for the epoch times between `iat` and `exp`.

...But wait, how do we know all of this? Isn't it encrypted into something unreadable? JWT isn't used that way; it is meant to be readable by anyone, even if they don't know the secret value. Instead, JWT ensures that the payload isn't edited by anyone who does not know the secret value. 

In the first (header) part, the `alg` field is set to `HS256`, which is HMAC using SHA-256. As you can guess from its name, it ensures that the payload isn't edited by hashing the payload together with the secret value. The third part of the JWT is the resulting hash.

In other words, if you know the secret value, you can craft your own JWT and bypass the username check. Our next goal is to find out how.

### Getting `jwt_secret.txt`

`JWT_SECRET` is saved in the file `static/jwt_secret.txt`. 

```python
if not os.path.exists("static/jwt_secret.txt"):
    JWT_SECRET = random.randbytes(32).hex()
    with open("static/jwt_secret.txt", "w") as f:
        f.write(JWT_SECRET)
else:
    with open("static/jwt_secret.txt") as f:
        JWT_SECRET = f.read()
```

In Flask, all the files under `static/` are accessible. Therefore, if you visit `http://34.170.146.252:28215/static/jwt_secret.txt`, you can view the secret value!

You can check that the secret value is valid using jwt.io.

![alt text](image.png)

### Getting the flag!

Now, craft your own JWT using JWT Encoder in jwt.io. (Or, you can use PyJWT like [my solver](./solver.py).)

![alt text](image-2.png)

Then, replace the token in the cookie in the application tab, and reload the page.

![alt text](image-3.png)

### Flag

`Alpaca{Br3w_your_own_4dmin_JWT}`
