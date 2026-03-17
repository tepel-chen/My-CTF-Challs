# Another Login Challenge

[English](./README.md)

## 説明

ログイン! ログイン! ログイン!

### 初心者向けヒント1

- `index.js` では、簡易的なログイン機能が実装されています。
- `users[username]`が存在することと、`users[username].password`が与えられたパスワードと一致することを確認しているようです。
- 自分でユーザーを作ることはできなさそうです。また、`admin`というユーザーが登録されていますが、そのパスワードを推測することも不可能でしょう。

</details>

### 初心者向けヒント2

- Javascriptでは、`users["foobar"]`と`users.foobar`はおおよそ同値です。これを利用できないでしょうか？
- ログイン画面の機能だけでは意図したデータを送れないかもしれません。ブラウザ以外の方法でデータを送る方法については、[I wanna be the AdminのWriteup](https://github.com/tepel-chen/My-CTF-Challs/blob/main/Daily%20AlpacaHack/I%20wanna%20be%20the%20Admin/README-ja.md) を参考にしてください。


## Writeup

### 概要

```javascript
let users = {
  admin: {
    password: crypto.randomBytes(32).toString("base64"),
  },
};

/* ... */

app.post("/", (req, res) => {
  const { username, password } = req.body;
  const user = users[username];
  if (!user || user.password !== password) {
    return res.send("invalid credentials");
  }

  res.send(FLAG);
});
```

この問題の目的はログインに成功することです。存在しているユーザーは `admin` だけに見えますが、パスワードの推測は現実的ではありません。

### 解法

通過するべきチェックは2つあります。`user` が `undefined` や `null` ではないことと、`user.password` が送信したパスワードと一致することです。順に見ていきましょう。

JavaScript では `users["admin"]` と `users.admin` はほぼ同等です。また、JavaScript のオブジェクトは `Object`クラスのインスタンスなので、そのメンバーやメソッドにアクセスできます。

例えば `users.constructor` は `Object` のコンストラクタ関数を返します。先述の仕様と組み合わせると `users["constructor"]` も同じ値を返すことがわかります。これは `undefined` でも `null` でもないため、`username="constructor"` とすれば1つ目のチェックを通過できます。

そうすれば2つ目のチェックの回避も簡単です。`user.password` は `undefined` なので、`password` を送らなければ一致判定を通せます。

完全な exploit は [solver.py](./solution/solve.py) を参照してください。

## フラグ

`Alpaca{Javascr1pt_is_a_st4nge_languag3...}`
