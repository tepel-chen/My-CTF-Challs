# Log Viewer

[English version](./README.md)

## 問題文

正規表現機能を備えたシンプルなログビューア。

## Writeup

### 問題概要

脆弱性の本体は次の部分です。

```python
query = request.form.get("query", "")

command = ["awk", f"/{query}/", "info.log"]
result = subprocess.run(
    command,
    capture_output=True,
    timeout=0.5,
    text=True,
)
log = result.stderr or result.stdout
```

`awk`コマンドは、ファイルを1行ずつ処理する用途でよく使われます(例：フィルタリングや変換)。ここではユーザー入力が`f"/{query}/"`に埋め込まれており、これが`awk`の「プログラム」として渡されます。つまり、`awk`のプログラムに対してインジェクションが可能です。

フラグは`/flag-<フラグのmd5ハッシュ>`に存在します。このインジェクションを使ってファイル内容を取得できるでしょうか？

### OS コマンドインジェクションの理解

一見すると、`foobar/ info.log; cat /flag* #`のようなペイロードが動きそうに見えます。というのも、注入後のコマンドが次のようになると想像してしまうからです。

```bash
awk /foobar/ info.log; cat /flag* # / info.log
```

しかし、これは動きません。理由は「シェル(例：bash)を介して実行されるOSコマンド」と「シェルを介さずに実行されるOSコマンド」には違いがあるためです。

Pythonでシェル経由の代表例は`os.system`です。もしコードが次のようになっていれば、

```python
os.system(f"awk /{query}/ info.log")
```

先ほどのペイロードは成立していた可能性があります。

コマンドがシェル経由で実行される場合、攻撃者は他にも次のような手法を使えます。

- `;`や`&`、`|`によるコマンド分割
- `$(command)`や`` `command` ``によるコマンド置換
- `$ENV`のような環境変数参照

一方、シェルを介さずに実行されるコマンドでは、これらは解釈されません。そのため任意コマンド実行が難しくなります。`subprocess.run`は`shell=True`を指定した場合のみシェル経由で実行されますが、今回はそうではありません。よって別のアプローチが必要です。

### `awk`の理解

`awk`の使い方を調べると、これは単なるテキスト処理ツールではなく、プログラミング言語でもあることが分かります。`awk`では `/pattern/ { action }`という形式で処理を書けます。また、`awk`では`#`がコメント開始です。

したがって、例えば `.*/{print $1} #`というペイロードを送ると、引数は次のようになります。

```
/.*/{print $1} #/
```

ここで末尾の `/`は、サーバ側が入力を`f"/{query}/"`で包むことによって必ず付与されるものです。そのため、この末尾の`/`が注入した `awk` プログラムの邪魔にならないよう、`#`を付けてコメントアウトする必要があります。

有用な関数については [`awk`のマニュアル](https://www.gnu.org/software/gawk/manual/html_node/Functions.html) を読むのも手ですが、このような状況ではもっと簡単に使える情報源があります。

[GTFOBins](https://gtfobins.github.io/) は、ローカルの制限を回避するために使えるバイナリとペイロード例を集めたサイトです。[GTFOBins の `awk`ページ](https://gtfobins.github.io/gtfobins/awk/)には、次のように`system()`を使ってシェルを起動できる例が載っています。

```awk
system("/bin/sh")
```

したがって、`.*/{system("cat /flag*")} #`を送れば、`cat /flag*`が実行されます。しかし、このままでは結果ではなくエラーページを表示してしまいます。これは、`subprocess.run`で500 msのタイムアウトを設定しており、`system()`コマンドを2000回実行するとなると、このタイムアウトに引っかかってしまうためです。

これを回避する方法としては次のどちらかが有効です。

- マッチする行を1行に絞る(例：`242.24.138.42/{system("cat /flag*")} #`)
- フラグを出力したら `exit` で `awk` を終了する(例：`.*/{system("cat /flag*"); exit 0} #`)

## Flag

`Alpaca{th3_AWK_Pr0gr4mming_Lan9u4g3}`