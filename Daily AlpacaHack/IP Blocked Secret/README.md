# IP Blocked Secret

[日本語はこちら](./README-ja.md)

## Description

The secret is safer than ever!

### Beginner Hint

- This challenge is about **SQL Injection**
- If you are not familiar with SQL Injection, we recommend solving [Xmas Login](https://alpacahack.com/daily/challenges/xmas-login) first.

## Writeup

`POST /set` saves a secret to your session. The data is stored in a SQLite database, along with the IP address of the creator.

```python
IPV4_RE = re.compile(r"\d{,3}.\d{,3}.\d{,3}.\d{,3}", re.ASCII)
# ...
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
```

You can view the secret by sending a `GET` request to `/`. However, you must have the same IP address as when you created the secret. 

```python
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
```

The goal of this challenge is to retrieve the flag from the `flag` column in the `flag` table.

### Step 1: Finding the SQL Injection

The SQL queries in this application do not use prepared statements, making them potentially vulnerable to SQL injection if inputs are not properly escaped.

In `GET /`, the `sid` parameter is not escaped, but you cannot control its value because it is assigned by the server.

In `POST /set`, the `secret` parameter is escaped as follows:

```python
secret = secret.replace("'", "''")
```

This is the correct way to escape single quotes in SQLite, so there is likely no way to perform SQL injection through this parameter. (However, escaping strings manually is generally considered an incorrect way to prevent SQL injection; you should always use placeholders/parameterized queries instead.)

The remaining attack vector is the `ip` parameter in `POST /set`. You can easily spoof your IP address using the `X-Forwarded-For` header. However, it must match the following regular expression:

```python
re.compile(r"\d{,3}.\d{,3}.\d{,3}.\d{,3}", re.ASCII)
```

There are multiple issues with this validation method, but the most significant one is that the `.` character is not escaped with a backslash. In regular expressions, an unescaped `.` matches any character. Additionally, since `\d{,3}` matches zero to three digits, this regular expression can match any 3-character string.

For example, if you set the `X-Forwarded-For` header (`ip`) to `'/*` and the `secret` to `*/,(SELECT flag FROM flag))--`, the resulting SQL query will be:

```sql
INSERT INTO secrets (ip, secret)
VALUES (''/*', '*/,(SELECT flag FROM flag))--')
ON CONFLICT(ip) ...
```

which simplifies to:

```sql
INSERT INTO secrets (ip, secret)
VALUES ('',(SELECT flag FROM flag))
ON CONFLICT(ip) ...
```

### Step 2: Exfiltrating the Flag

The previous payload does not work directly because the `ip` field in the database is set to an empty string, and `GET /` requires the client's IP to match it and also pass the IP address format validation (which an empty string does not).

There are several ways to exfiltrate the flag. Writeups by [baumroll1234](https://github.com/baumroll0928-spec/myRepository/tree/main/Daily_AlpacaHack/m202607/d05_IP_Blocked_Secret) and [nirvana](https://sl9-1994.github.io/posts/ip_blocked_secret/) cover really clever ways to achieve this (thank you both for the great writeups!), but I will cover some alternative approaches.

#### Step 2-a: Error-Based Injection

If you set the IP to `'/*` and the `secret` to `*/,(SELECT flag FROM flag WHERE 1=0))--`, the database will raise an error because the `secret` column cannot be `NULL`. However, if you set the `secret` to `*/,(SELECT flag FROM flag WHERE 1=1))--`, it will execute successfully without raising an error. Using this boolean oracle, you can determine whether a specific condition is met.

You can extract the character code of the n-th character of the flag using `unicode(substr(flag, n, 1))`. This allows you to leak the flag character by character.

Please see the full solve script in [solver1.py](./solver1.py).

#### Step 2-b: Leaking the Flag Directly

Notice that both `111'/*` and `111` match the IP regular expression. If you set the IP to `111'/*` and the `secret` to `*/,(SELECT flag FROM flag))--`, the inserted record will have an `ip` of `111`. Therefore, you can retrieve this secret by making a `GET /` request with the `X-Forwarded-For` header set to `111`.

Please see the full solve script in [solver2.py](./solver2.py).

## Flag

`Alpaca{ke3p_the_Secret_t0_yours3lf}`
