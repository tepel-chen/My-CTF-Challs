# Personal Website - secured

## 問題文

I heard my website isn't secure. I made it persistent by using a database so that I can recover it if something goes wrong.

## Writeup

Class Pollutionと深さ制限のバイパスについては[Personal Website](/Full Weak Engineer CTF 2025/Personal Website)をご覧下さい

shelveはユーザーオブジェクトを[pickleでシリアライズ・デシリアライズする](https://github.com/python/cpython/blob/v3.13.6/Lib/shelve.py#L114)。pickleは利用方法によってはRCEが可能なほど強力な仕組みであるため、ここにガジェットが無いかを探す。

### うまくいかない方法1: オペコードの変更

[pickle.py](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py)を読むとたくさんのグローバル変数が定義されているため、どれかを変えたらうまく行きそうな雰囲気はある。例えば、オペコードの文字を変えることによって、シリアライズ時とデシリアライズ時でオペコードの解釈が変わり、RCEが可能になるような解法を考えるかもしれない。

残念ながら、この解法はうまくいかない。これは、`pickle.py`に記載されている実装は実際はフォールバックで、ほとんどの場合は[Cで実装されたpickle.c](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1819)が利用されるためである。Cで実装されたpickleはオペコードがハードコードされているため、Class Pollutionでは書き換えることができない

### うまくいかない方法2: `__qualname__`の変更

[`save_global`の実装](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1072)を読むと、pickleではオブジェクトのクラスを参照する際に、`obj.__module__`と`obj.__qualname__`を利用していることがわかる。したがって、例えば、`obj.__module__ = 'subprocess'`と`obj.__qualname__ = 'Popen'`とすれば、デシリアライズされたときのクラスが`subprocess.Popen`にできるようになると考えるかもしれない。

残念ながら、この解法もうまくいかない。なぜなら、シリアライズする際に、`__module__`と`__qualname__`を利用してインポートしたクラスが、シリアライズするオブジェクトのクラスと一致するかをチェックし、しなかった場合エラーになるからである。

### Step1: `fix_imports`の利用

pickleはバージョンが0から5まであるが、プロトコルバージョン2以前はPython 2向けの実装である。そして、プロトコルバージョン2以前の場合、インポートするクラスがPython 2とPython 3で異なってしまう場合の[差分を修正するコード](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1150)が実行される。また、これは「うまくいかない方法2」で説明した同一性チェックの後に行われるため、うまくいけばデシリアライズされるクラスを変えることができそうである。

この際に`_compat_pickle`というモジュールのグローバル変数が利用されるが、これは、[_pickle.cでもcompat_pickleからインポートして使われる](https://github.com/python/cpython/blob/v3.13.6/Modules/_pickle.c#L344)ため、これらをClass pollutionで変更することが可能である。

また、shelveでは、[インスタンス化のたびに`DEFAULT_PROTOCOL`を参照してプロトコルバージョンを決定する](https://github.com/python/cpython/blob/v3.13.6/Lib/shelve.py#L88)ため、バージョンもClass pollutionで変更することが可能である。

もし、
```python
_compat_pickle.REVERSE_NAME_MAPPING[("user", "User")] = ("subprocess", "Popen")
```
のように変更できたら、`subprocess.Popen`としてデシリアライズされるようになるが、辞書のキーがタプルになっているため、今回のClass Pollutionでは変更できない。

代わりに、
```python
_compat_pickle.REVERSE_IMPORT_MAPPING["user"] = "subprocess"
```
と変更することで、`subprocess.User`というクラスがインポートされるようになる。しかし、`user.User`以外に`User`というクラスはすでにインポートされておらず、新しいクラスのインポートはaudit hookによって禁止されているため、この手法だけではRCEはできない。

### Step2: 改行インジェクション

プロトコルバージョン2以前と3以降ではクラスをシリアライズしたときの記法が異なる。プロトコルバージョン2では

```python
    self.write(GLOBAL + bytes(module_name, "ascii") + b'\n' +
                bytes(name, "ascii") + b'\n')
```

のように[シリアライズ](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1158)され、

```python
    def load_global(self):
        module = self.readline()[:-1].decode("utf-8")
        name = self.readline()[:-1].decode("utf-8")
        klass = self.find_class(module, name)
        self.append(klass)
    dispatch[GLOBAL[0]] = load_global
```
のように[デシリアライズ](https://github.com/python/cpython/blob/v3.13.6/Lib/pickle.py#L1569)される。この時、`module_name`に改行が含まれていないことをチェックしていないため、改行が含まれる場合は、デコード時に改行以前の文字列をモジュール名、それ以降をクラス名として扱う。それ以降は別のオペコード・オペランドとして扱うため、これで任意のpickleを実行できるようになる。


### 余談

`sys.addaudithook`によるチェックは、開催直前まで存在していませんでした。

一週間前のHITCON CTF 2025の[`simp`](https://blog.splitline.tw/hitcon-ctf-2025-authors-write-up/#misc-simp)というチャレンジは以下のようなjailでした。

```python
#!/usr/local/bin/python3
while True:
    mod, attr, value = input('>>> ').split(' ')
    setattr(__import__(mod), attr, value)
```

任意のモジュールを読み込み、属性に任意の文字列を設定できる、という問題で、この問題とかなりテーマが近いことがわかります。「うまくいかない方法2: `__qualname__`の変更」の手法を使えば、任意のモジュールをロードすることができるため、この問題では対話型シェルが使えないという問題を除けば、ほぼ同じ問題に帰着することができました。

実際に非想定の解法を見つけられましたが、ガジェットを探す難易度はあまり変わらないな、という印象でした。しかし、開催直前のCTFで、この問題を見たか見てないかで難易度が大きく変わるのは不都合だと考え、急遽`sys.addaudithook`を利用して封じました。

ぜひ、`sys.addaudithook`が無い場合の解法も探してみて下さい。ヒントとしては、この解法ではバージョンを下げる必要がないため、shelve以外のpickleを利用するシステムでもうまく行く(ただしpickleでオブジェクトがシリアライズ・デシリアライズされる必要がある)という利点があります。

## Flag

`fwectf{placeholder_<dynamic>}`



