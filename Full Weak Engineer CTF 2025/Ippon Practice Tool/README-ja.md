# Ippon Practice Tool

## 問題文

[IPPON!!!](https://note.com/asusn_online/n/na7d53db7037f)

Flag format: `fwectf\{[a-z0-9_!?]+\}`.

## Writeup

`GET /answer/:id`で、HTMLインジェクションが可能であるが、CSPがあるため、XSSやCSSインジェクションは不可能だ。

```ts
app.use((req: Request, res: Response, next: NextFunction) => {
  res.locals.nonce = crypto.randomBytes(32).toString("hex");
  res.setHeader(
    "Content-Security-Policy",
    `default-src 'self'; img-src *; script-src 'none'; style-src 'nonce-${res.locals.nonce}'`
  );
  next();
});
```

`GET /search?q=`を利用してフラグがヒットした場合としなかった場合をHTMLインジェクションのみで外部にリークできるだろうか？


フラグがヒットしなかった場合は次のようになっている。
```ts
  if (q.length === 0) {
    return res.end("<html><body>Invalid query. <a href='/'>Home</a></body></html>");
  }
```
`res.end`を利用すると`Content-Type`ヘッダーが送信されない。(送信するためには`res.send`を利用する。)つまり、HTMLインジェクションで`Content-Type`が送信されたかどうかを判定することができるか？という問題に帰着できる。

これを判定するには[`<object>`タグ](https://developer.mozilla.org/ja/docs/Web/HTML/Reference/Elements/object)を利用できる。Firefoxでは`type`という属性を利用すると、`Content-Type`が送信されなかった場合にその属性のtypeとして解釈させることが可能である。(Chromiumでは、`Content-Type`が送信されなかった場合に`text/plain`として解釈されるため、以下の手法は使えない。)それに対して、`Content-Type`が送信された場合はそちらが優先されるという仕様である。

そして、`<object>`タグは、何かしらの理由で要素を表示できなかった場合に、フォールバックを指定できる。この「何かしらの理由」には、「画像のレンダリングの失敗」も含まれる。したがって、`type=image/png`とすると、`Content-Type`が指定されなかった場合には画像として読み込もうとして失敗しフォールバックが発生し、Content-Typeが指定された場合には、HTMLとして読み込まれるためフォールバックが発生しない。

フォールバックが発生したかどうかの判定は、[`img`タグのlazy loadingを利用する](https://infosec.zeyu2001.com/2023/from-xs-leaks-to-ss-leaks#lazy-loading)方法が知られている。img-srcのCSPは`*`のため、この情報を自分のサーバーへリークすることができる。

## Flag

`fwectf{c4nt_wa1t_4_a5usn_c7f_3}`

