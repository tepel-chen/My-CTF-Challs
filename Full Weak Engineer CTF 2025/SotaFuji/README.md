# SotaFuji

## Description

Sota Fuji Fun club

## Writeup

We want to obtain the flag via request smuggling. The Go server is likely to interpret requests according to [RFC 7230](https://www.rfc-editor.org/rfc/rfc7230.html).
Therefore, the idea is to exploit RFC violations in the proxy server to successfully perform request smuggling.
The proxy server has **three** RFC violations.

### 1. When multiple Content-Length headers exist, the latter is used

According to [RFC 7230 3.3.3.4](https://www.rfc-editor.org/rfc/rfc7230.html#section-3.3.3)

> If a message is received without Transfer-Encoding and with
       either multiple Content-Length header fields having differing
       field-values or a single Content-Length header field having an
       invalid value, then the message framing is invalid and the
       recipient MUST treat it as an unrecoverable error.

Thus, if multiple Content-Length headers are present, the correct behavior is to return an error. The Go server is implemented correctly, so on its own this only results in an error on the Go side. Therefore, it must be combined with the next bug.

### 2. Header field names are `.trim()`-ed

According to [RFC 7230 3.2](https://www.rfc-editor.org/rfc/rfc7230.html#section-3.2), headers are defined as follows, and there is no basis for applying `.trim()` to field names:

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

As seen in the obs-fold definition:

```
X-Foo: bar
 biz
```

the line `biz` should be treated as part of the previous header. Although this specification is now obsolete, the Go server still interprets it for backward compatibility.

Therefore:

```
X-Foo: bar
 Content-Length: 20
```

will be interpreted by the Go server as `X-Foo` with the value `bar Content-Length:20`, but the proxy server interprets it as two headers: `X-Foo` and `Content-Length`.

Combining this with the first bug:

```
GET / HTTP/1.1
Host: localhost:4000
Content-Length: 0
X-Data: a
 Content-Length: 40

GET /flag HTTP/1.1
Host: localhost:4000
```

The Go server interprets the `Content-Length` as 0, while the proxy interprets it as 40.
This discrepancy allows request smuggling to succeed.

At this point, we can send a request to `/flag`, but we still cannot retrieve the response. To do so, we must use the final bug.

### 3. If a `Content-Length` header exists in the response, the proxy always assumes there is a body

For `HEAD` requests, the server returns the `Content-Length` of the corresponding `GET` response, but does not return a body. Thus, it is an RFC violation for the proxy to assume a body must always exist if `Content-Length` is present.

By sending a `HEAD` request to `/`, the response will include a `Content-Length` header (the length of the `GET` body) but no body.
As a result, the proxy treats the subsequent `/flag` request as the body, allowing the flag’s contents to be retrieved.

### Unintended Solution

According to [claustra01's writeup](https://zenn.dev/claustra01/articles/7b116f8d542cc4#%5Bweb%2C-medium%5D-sotafuji-(1-solve%E2%9C%A8)), the Go server also accepts` \n` as a line break in place of `\r\n`. This behavior can also be exploited for a desync-based attack.

## Flag

`fwectf{pr0_sh0G1_Ki5hI_N07_g0_kI5H1}`

