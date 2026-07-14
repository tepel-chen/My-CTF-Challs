# IP Blocked Secret

[English](./README.md)

## 問題文

これまで以上に安全です！

### Beginner Hint

- この問題は **SQL インジェクション** の脆弱性を利用する問題です。
- SQL インジェクション について詳しく知らない場合は、[Xmas Login](https://alpacahack.com/daily/challenges/xmas-login) を先に解くことをおすすめします

## Writeup

`POST /set` はセッションにシークレットを保存します。データは作成者のIPアドレスとともにSQLiteデータベースに格納されます。

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

`/` に `GET` リクエストを送信することでシークレットを表示できます。ただし、シークレット作成時と同じIPアドレスである必要があります。

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

このチャレンジの目的は、`flag` テーブルの `flag` カラムを取得することです。

### ステップ 1: SQLインジェクションの探索

このアプリケーションのSQL文はプリペアドステートメントを使用していないため、値が適切にエスケープされていない場合、SQLインジェクションに対して脆弱になる可能性があります。

`GET /` では `sid` はエスケープされていませんが、サーバーによって割り当てられるため、その内容を制御することはできません。

`POST /set` では、`secret` は以下のようにエスケープされています。

```python
secret = secret.replace("'", "''")
```

これはSQLiteにおいてシングルクォートをエスケープする正しい方法であるため、このパラメータからSQLインジェクションを実行することはほぼ不可能です。（ただし、文字列を個別にエスケープする手法はSQLインジェクションを防ぐ方法としては推奨されません。プリペアドステートメントのプレースホルダーを使用すべきです。）

最後に残された攻撃対象は、`POST /set` 内の `ip` パラメータです。`X-Forwarded-For` ヘッダを使用することで、IPアドレスを容易に偽装できます。しかし、値は以下の正規表現にマッチする必要があります。

```python
re.compile(r"\d{,3}.\d{,3}.\d{,3}.\d{,3}", re.ASCII)
```

このIPアドレスのチェック方法には多くの問題がありますが、最大の原因は **`.` がバックスラッシュでエスケープされていないこと**です。正規表現において、エスケープされていない `.` は任意の1文字にマッチします。さらに、`\d{,3}` は0文字から3文字の数字にマッチするため、この正規表現は任意の3文字の文字列にマッチさせることができます。

例えば、`X-Forwarded-For` ヘッダ（`ip`）を `'/*` に設定し、`secret` を `*/,(SELECT flag FROM flag))--` に設定した場合、生成されるSQLは以下のようになります。

```sql
INSERT INTO secrets (ip, secret)
VALUES (''/*', '*/,(SELECT flag FROM flag))--')
ON CONFLICT(ip) ...
```

これは以下のように解釈されます。

```sql
INSERT INTO secrets (ip, secret)
VALUES ('',(SELECT flag FROM flag))
ON CONFLICT(ip) ...
```

### ステップ 2: フラグの抽出

上記のペイロードをそのまま使うだけでは機能しません。データベース内の `ip` フィールドが空文字（`''`）になってしまう一方で、`GET /` を呼び出すためにはクライアントのIPがその値と一致し、なおかつIPアドレスのフォーマット検証を通過する必要があるからです（空文字は検証を通過しません）。

フラグを抽出する方法はいくつかあります。[baumroll1234](https://github.com/baumroll0928-spec/myRepository/tree/main/Daily_AlpacaHack/m202607/d05_IP_Blocked_Secret) 氏や [nirvana](https://sl9-1994.github.io/posts/ip_blocked_secret/) 氏のWriteupでは、これを達成するための方法が紹介されています（素晴らしいWriteupを書いてくださりありがとうございます！）。ここでは、それらとは異なるいくつかのアプローチを解説します。

#### ステップ 2-a: エラーベースインジェクション (Error-Based Injection)

IPを `'/*` に、`secret` を `*/,(SELECT flag FROM flag WHERE 1=0))--` に設定した場合、`WHERE 1=0` 条件によって行が返らないため `secret` カラムが `NULL` になり、データベースはエラーを発生させます。一方で、`secret` を `*/,(SELECT flag FROM flag WHERE 1=1))--` に設定した場合はエラーを起こさずに正常終了します。この動作の違い（オラクル）を利用して、特定の条件が満たされているかどうかを判定できます。

`unicode(substr(flag, n, 1))` を使うことでフラグの n 文字目の文字コードを取得できるため、これを利用して1文字ずつフラグを特定していくことができます。

完全な攻略スクリプトについては、[solver1.py](./solver1.py) を参照してください。

#### ステップ 2-b: フラグの直接リーク

`111'/*` と `111` はどちらもIPアドレスの正規表現にマッチします。IPを `111'/*` に、`secret` を `*/,(SELECT flag FROM flag))--` に設定すると、挿入されるレコードの `ip` は `111` になります。したがって、`X-Forwarded-For` ヘッダに `111` を指定して `GET /` にアクセスすることで、このシークレット（フラグの内容）を直接取得できます。

完全な攻略スクリプトについては、[solver2.py](./solver2.py) を参照してください。


## フラグ

`Alpaca{ke3p_the_Secret_t0_yours3lf}`
