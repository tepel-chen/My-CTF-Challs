# SotaFuji

## 問題文

Sota Fuji Fun club

## Writeup

Request Smugglingを利用してフラグを取得したいが、Goサーバーの方はおそらく[RFC 7230](https://www.rfc-editor.org/rfc/rfc7230.html)に則ってリクエストを解釈するだろう。したがって、`proxy`サーバーのRFC違反を利用してRequest Smugglingを成功させることを考える。`proxy`サーバーは3つのRFC違反がある。

### 1. Content-Lengthが複数ある場合、後者を採用する

[RFC 7230 3.3.3.4](https://www.rfc-editor.org/rfc/rfc7230.html#section-3.3.3)によると、
> If a message is received without Transfer-Encoding and with
       either multiple Content-Length header fields having differing
       field-values or a single Content-Length header field having an
       invalid value, then the message framing is invalid and the
       recipient MUST treat it as an unrecoverable error.

とあるため、Content-Lengthが複数ある場合はエラーを返すのが正しい挙動である。ただし、Goサーバーの方は正しく実装されているため、これだけではGoサーバーでエラーになるだけである。したがって次のバグと組み合わせる必要がある。

### 2. ヘッダーフィールド名が `.trim()` される

[RFC 7230 3.2](https://www.rfc-editor.org/rfc/rfc7230.html#section-3.2)によると、ヘッダーは以下のように表されるため、`.trim()`を行っても良い根拠はない。
```
header-field   = field-name ":" OWS field-value OWS
field-name     = token
field-value    = *( field-content / obs-fold )
field-content  = field-vchar [ 1*( SP / HTAB ) field-vchar ]
field-vchar    = VCHAR / obs-text

obs-fold       = CRLF 1*( SP / HTAB )
                    ; obsolete line folding
                    ; see Section 3.2.4
```

そして`obs-fold`の箇所をみてわかる通り、

```
X-Foo: bar
 biz
```
のように書いた場合、`biz`は前のヘッダーの一部として扱われるべきである。また、この仕様は廃止扱いだが、Goサーバーは後方互換性のため解釈する。

したがって、
```
X-Foo: bar
 Content-Length: 20
```
と書いた場合、Goサーバーは`X-Foo`の値が`bar Content-Length:20`であると解釈するのに対して、`proxy`サーバーは`X-Foo`と`Content-Length`であると解釈する。

これを1つ目のバグと組み合わせると

```
GET / HTTP/1.1
Host: localhost:4000
Content-Length: 0
X-Data: a
 Content-Length: 40

GET /flag HTTP/1.1
Host: localhost:4000

```
と送ることで、GoサーバーはContent-Lengthは0であると解釈し、proxyサーバーはContent-Lengthは40であると解釈するのでRequest Smugglingに成功する。

これにより、`/flag`にリクエストを送ることができるが、これではまだ結果を取得することができないので最後のバグを利用する。

### 3. レスポンスヘッダーに`Content-Length`がある場合は必ずBodyがあると想定する

リクエストが`HEAD`リクエストである場合、サーバーは`GET`リクエストが送られてきた場合の`Content-Length`を返すがBodyを返さないので、上記はRFC違反である。

`/`へのリクエストを`HEAD`にする事により、`GET`時に送られるべきBodyの長さの`Content-Length`が含まれるがBodyは無い状態になり、結果的に`/flag`へのリクエストをBodyとして扱ってしまうため、`/flag`の内容を取得することができる。


### 別解

[claustra01さんのwriteup](https://zenn.dev/claustra01/articles/7b116f8d542cc4#%5Bweb%2C-medium%5D-sotafuji-(1-solve%E2%9C%A8))によると、Goのサーバーは`\r\n`の代わりに`\n`でも改行として扱うので、これを利用したdesyncも利用できたようです。


## Flag

`fwectf{pr0_sh0G1_Ki5hI_N07_g0_kI5H1}`

