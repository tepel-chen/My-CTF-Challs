# Free Coupon

[English](./README.md)

## 問題文

今すぐ無料クーポンを手に入れて、割引価格でフラグを買おう！

### 初心者向けヒント1: この問題の概要</summary>

- ページにアクセスするとランダムなセッションID(`sid`)が割り当てられます。
- `/buy`のページアクセスしたときに、セッションIDに紐づいた残高(`balance`)が30以上であればフラグを「購入」して見ることができます。
- 残高の初期値は0ですが、`/redeem`のページにアクセスするとクーポンと引き換えに10の残高を得ることができます。しかし、その後に`redeemed`というフラグが`true`になってしまい、複数回クーポンを利用できないようになっていそうです。
- クーポン以外に残高を増やす方法はありません。

### 初心者向けヒント2: 問題へのアプローチ

- `/redeem`の実装は少し不自然です。アクセスすると数秒掛けてクーポンを取得するようですが、この仕様の隙をつくことはできないでしょうか？

## Writeup


### 概要

この問題の目標は、`balance` を 30 以上にして `/buy` にアクセスすることです。残高を増やす方法は、次のコードにあるクーポン引き換えだけです。

```javascript
app.get("/redeem", session, async (req, res) => {
  const { redeemed } = sessions.get(req.sid);
  res.setHeader("Content-Type", "text/html");

  res.write(`<!DOCTYPE html>
<html>
<body>
  <p>Checking if the coupon is valid...</p>`);
  await sleep(1000);

  if (redeemed) {
    return res.end(`You already redeemed your coupon.<a href="/">Home</a>`);
  }

  res.write(`<p>Updating your balance...</p>`);
  await sleep(1000);

  const { balance } = sessions.get(req.sid);
  sessions.set(req.sid, {
    redeemed: true,
    balance: balance + 10,
  });

  return res.end(`<p>Coupon redeemed successfully! Redirecting back to the main page...</p>
  <meta http-equiv="refresh" content="3;URL=/" />
</body>
</html>`);
});
```

この処理では、セッション ID に対応する `redeemed` フラグを `true` にし、同じクーポンの再利用を防ぐようなっています。1回の引き換えでは balance は 10 しか増えませんが、必要な値は 30 です。

### 解法

本質的な脆弱性は、**`redeemed` をチェックするタイミングと、残高を更新するタイミングの間に２秒のギャップがある**ことです。

そのため、`/redeem` にほぼ同時に 3 回アクセスすると、いずれも `redeemed` チェックを通過してしまいます。具体的には: 

* (t=0) `/redeem` への 3 リクエストがほぼ同時に処理される
* (t=0) 各リクエストが `sessions` から `redeemed` を読み、すべて `false` となる
* (t=1) 3 リクエストすべてが `if (redeemed)` を通過する
* (t=2, request 1) `redeemed` を `true` にし、`balance` は 10 になる
* (t=2, request 2) `redeemed` を `true` にし(つまり変更なし)、 `balance` は 20 になる
* (t=2, request 3) `redeemed` を `true` にし(つまり変更なし)、 `balance` は 30 になる

自動化する場合は [solve.py](./solution/solve.py) を参照してください。ブラウザでも `/redeem` を素早く 3 タブで開けば再現できます。

複数の処理が同時に走り、共有データが想定外の順序で更新されることで問題が起きる脆弱性は **race condition** と呼ばれます。

さらに今回のように、先に状態をチェックした後、実際に使うまでの間に状態が変化してしまう種類は **TOCTOU (Time-Of-Check to Time-Of-Use)** と呼ばれます。

## フラグ

`Alpaca{N0_such_thing_4s_a_fre3_lunch}`
