# Weakness in the Middle

## 問題文

That name is way too sus for just a proxy application, isn't it?

The instance will shut down after 3 minutes. 

## Writeup

mitmwebを起動すると、ポート8080にプロキシサーバーが、ポート8081に管理用UIのサーバーが起動するようになっている。問題では、ポート8080しか外部に解放されていないが、ポート8080をプロキシとしてポート8081にアクセスできる。ログインがパスワードで保護されているが、パスワードは問題より与えられるためログインできる。

mitmwebには[Commands](https://docs.mitmproxy.org/stable/concepts/commands/)という機能があり、データの加工などをコマンド形式で送ることができる。この中から有用なコマンドを探したい。

実際にmitmwebのGUIからOptions>Display Command Barを選択して、コマンドパレットを開くとコマンドの一覧が見れるので、怪しいものを探す。`scripts.run`という名前からして任意コード実行可能そうなコマンドが見つかるので、説明を見てみると、

> Argument suggestion: script.runflows path
> \# Run a script on the specified flows. The script is configured with the current options and all lifecycle events for each flow are simulated. Note that the load event is not invoked.

> 指定したフローに対してスクリプトを実行します。スクリプトは現在のオプションで設定され、各フローのすべてのライフサイクルイベントがシミュレートされます。ただし、load イベントは呼び出されない点に注意してください。

パスを指定して「実行」してくれるようだ。[ソースコード](https://github.com/mitmproxy/mitmproxy/blob/38a7ee9867f9c472a7557c511bed487e18e96ebf/mitmproxy/addons/script.py#L34)を確認したり実験したりすることにより、pythonコードを実行してくれることがわかる。したがって、どこかにpythonファイルを書き込むことができれば、そのパスを指定することにより実行できることがわかる。

ファイルを保存するために、`save`と名のつくコマンドを見てみる。`options.save`、`save.file`、`save.har`などは、いずれも形式がPythonコードとして解釈できないため利用できない。

`cut.save`の説明を見てみるとこのようになっている。

> Argument suggestion: cut.save flows cuts path
> \# Save cuts to file. If there are multiple flows or cuts, the format is UTF-8 encoded CSV. If there is exactly one row and one column, the data is written to file as-is, with raw bytes preserved. If the path is prefixed with a "+", values are appended if there is an existing file.

> cutをファイルに保存します。flowやcutが複数ある場合、形式はUTF-8エンコードされたCSVになります。もし行と列がそれぞれ1つだけであれば、そのデータはそのまま（生のバイト列を保持した状態で）ファイルに書き込まれます。パスが「+」で始まっている場合、既存ファイルがあればその末尾に追記されます。

ここで、[flow](https://docs.mitmproxy.org/stable/addons/commands/#working-with-flows)とは通信の履歴を指し、[flow filter](https://docs.mitmproxy.org/stable/concepts/filters/)で指定することができるようだ。cutsについては詳細のドキュメントがなかったが[flowの要素を抽出する、pythonで言うところのgetattr](https://github.com/mitmproxy/mitmproxy/blob/38a7ee9867f9c472a7557c511bed487e18e96ebf/mitmproxy/addons/cut.py#L31)を行う操作のようだ。そして、この結果が1つとなった場合CSVではなくそのデータ自体を保存するとある。

したがって、次のステップでRCEを行う。

1. プロキシを通して、`http://attacker.com/pwn.py`へのリクエストを行う。このときの中身は、フラグを自分のサーバーに送るpythonコードである。
2. `cut.save`コマンドで、flowsを`~d attacker.com`、cutを`response.txt`、パスを`/tmp/pwn.py`で実行する。このとき、flowsの結果が一つならば、1.のレスポンスの中身がそのまま`/tmp/pwn.py`に書き出される。
3. `script.run`で`/tmp/pwn.py`を指定し、フラグを自分のサーバーに送る。

### 別解

[st98さんのwriteup](https://nanimokangaeteinai.hateblo.jp/entry/2025/08/31/213843#Web-500-Weakness-in-the-Middle-1-solves)によると、`cut.save`の代わりに`export.file`を利用してファイルを書き込むこともできたようだ。この場合、HTTPリクエストがそのまま書き出されるが、HTTPリクエストとPythonのpolyglotを作成することによりコード実行を成功させている。すごい。

## Flag

`fwectf{m17m_4774ck_15_unr31473d_LOL}`

