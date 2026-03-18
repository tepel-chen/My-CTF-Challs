# Free Coupon

[日本語はこちら](./README-ja.md)

## Description

Get a free coupon now and buy the flag at a discount!
### Beginner Hint 1: Overview of the problem (AI-translated)

- When you access the page, a random session ID (`sid`) is assigned.
- When you access the `/buy` page, if the balance associated with the session ID is 30 or more, you can "purchase" and view the flag.
- The initial balance is 0, but accessing the `/redeem` page allows you to get 10 balance in exchange for a coupon. However, after that, the `redeemed` flag becomes `true`, and it looks like you can't use the coupon multiple times.
- There is no way to increase the balance other than coupons.

### Beginner Hint 2: Approach to the problem (AI-translated)

- The implementation of `/redeem` is a bit unnatural. It takes a few seconds to get the coupon when accessed, but can we exploit this specification?

## Writeup

### Overview

The goal of this challenge is to access `/buy` with balance more than 30. The only way is to redeem a coupon in the following code:

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

This code sets the `redeemed` flag for your session ID to `true`, which is intended to prevent redeeming the same coupon more than once. A single redemption gives only 10 balance, but we need 30. How can we get there?

### Solution

The core vulnerability is that **there is a timing gap between checking `redeemed` and updating the balance**.  
So, if we hit `/redeem` three times in quick succession, all three requests can pass the check before any of them marks the coupon as redeemed. Here's how it works:

* (t=0) Three `/redeem` requests are processed almost simultaneously.
* (t=0) Each request reads `redeemed` from `sessions`; all of them see `false`.
* (t=1) All three requests pass the `if (redeemed)` check.
* (t=2, request 1) `redeemed` is set to `true`, and `balance` becomes 10.
* (t=2, request 2) `redeemed` is set to `true`, which already is, and `balance` becomes 20.
* (t=2, request 3) `redeemed` is set to `true`, which already is, and `balance` becomes 30.

You can automate this with [solve.py](./solution/solve.py), or open `/redeem` quickly in three browser tabs.

A vulnerability where multiple operations run concurrently and shared data changes in an unexpected way, as in this challenge, is called a **race condition**. More specifically, a race condition where code first checks state, but the state changes before the main operation runs, is called **Time-Of-Check to Time-Of-Use (TOCTOU)**.

## Flag

`Alpaca{N0_such_thing_4s_a_fre3_lunch}`
