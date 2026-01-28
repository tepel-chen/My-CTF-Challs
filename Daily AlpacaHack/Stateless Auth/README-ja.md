# Stateless Auth

## 説明

データベースなんて必要ない！

## 解説

### 概要

`/login` エンドポイントにユーザー名を送信すると、入力した名前を含む**JWT（JSON Web Token）**が発行されます。ただし `admin` をユーザー名として使うことはできません。

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

`/dashboard` にアクセスして `admin` というユーザー名のトークンがあると、フラグを取得できます。

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

### JWT の仕組み

JWT とは何でしょうか？ クッキーに保存されているトークンを見ると、以下のようになっています。

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiaWF0IjoxNzY5NjEwODg1LCJleHAiOjE3Njk2MTQ0ODV9.oy4uCRSwvCnq4q7sUpFrNLsJFGlP2tghj38JRFVpcx0
```

3 つの部分に `.` で区切られており、それぞれが Base64 でエンコードされています。各部分を視覚化したいときは [jwt.io](https://www.jwt.io/) を利用すると便利です。

![alt text](image-1.png)

2 番目の部分はペイロードで、`sub`（ユーザー名）、`iat`、`exp` を含む JSON です。トークンは `iat` と `exp` の間のエポック時間のみ有効です。

「どうしてペイロードの中身がわかるの？」と思うかもしれません。これは、JWT は暗号化するわけではなく、秘密鍵を知っていても読み取れるように設計されているからです。JWTは、秘密鍵を知らない人が内容を書き換えようとしても不正だとバレるよう、署名によって保護されています。

最初のヘッダー部では `alg` フィールドが `HS256`（HMAC using SHA-256）に設定されています。名前の通り、秘密鍵とペイロードを一緒にハッシュすることで改ざんを防ぎます。JWT の 3 番目の部分がそのハッシュです。

逆に言えば、秘密鍵の値がわかれば自分で JWT を作ることができます。そして、ユーザー名チェックをすり抜けられるのです。次のステップはその方法の解明です。

### `jwt_secret.txt` の取得

`JWT_SECRET` は `static/jwt_secret.txt` に保存されています。

```python
if not os.path.exists("static/jwt_secret.txt"):
    JWT_SECRET = random.randbytes(32).hex()
    with open("static/jwt_secret.txt", "w") as f:
        f.write(JWT_SECRET)
else:
    with open("static/jwt_secret.txt") as f:
        JWT_SECRET = f.read()
```

`static/main.css` が公開されていることからもわかるように、Flaskでは`static/` 以下のファイルはすべて配信されます。つまり `http://34.170.146.252:28215/static/jwt_secret.txt` にアクセスすれば、秘密鍵の値を確認できます。

この値が正しいことは jwt.io で検証できます。

![alt text](image.png)

### フラグの取得

jwt.io にある JWT Encoder を使って JWT を自作します。（あるいは [solver.py](./solver.py) のように PyJWT を使っても構いません。）

![alt text](image-2.png)

その後、ブラウザのアプリケーションタブでクッキーのトークンを差し替えてページを再読み込みするとフラグが表示されます。

![alt text](image-3.png)

### フラグ

`Alpaca{Br3w_your_own_4dmin_JWT}`
