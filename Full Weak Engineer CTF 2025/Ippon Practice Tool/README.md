# Ippon Practice Tool

## Description

[IPPON!!!](https://note.com/asusn_online/n/na7d53db7037f)

Flag format: `fwectf\{[a-z0-9_!?]+\}`.

## Writeup

It is possible to perform HTML injection via GET `/answer/:id`. However, because of the CSP, neither XSS nor CSS injection is possible.

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

Using only HTML injection, is it possible to leak to an external server whether the flag was hit or not in  `GET /search?q=`?

If the flag was not hit, the response is sent like this:

```ts
  if (q.length === 0) {
    return res.end("<html><body>Invalid query. <a href='/'>Home</a></body></html>");
  }
```

When `res.end` is used, the `Content-Type` header is not sent. (To send it, you would need to use `res.send` instead.) Thus, the problem resolves to whether we can detect if a `Content-Type` header was sent or not via HTML injection.

This can be done using the [`<object>` tag](https://developer.mozilla.org/ja/docs/Web/HTML/Reference/Elements/object) tag. In Firefox, when the `type` attribute is used, if the response has no `Content-Type` header, the specified type attribute will be applied instead. (In Chromium, when there is no `Content-Type` header, the response is treated as `text/plain`, so the following technique does not work.) If a `Content-Type` header is sent, that value takes precedence.

The `<object>` tag also allows specifying a fallback if the element cannot be displayed for some reason. One such reason includes failure to render an image. Therefore, by setting `type=image/png`, if no `Content-Type` is specified, the browser tries to load it as an image, and the fallback is triggered because it fails. If the Content-Type is specified, it is parsed as HTML, and the fallback is not triggered.

Whether the fallback occurred can be leaked to external server using  [lazy loading with an `img` tag](https://infosec.zeyu2001.com/2023/from-xs-leaks-to-ss-leaks#lazy-loading). Since CSP allows `img-src *`, this information can be leaked to an external server.

## Flag

`fwectf{c4nt_wa1t_4_a5usn_c7f_3}`

