# Another Login Challenge

## Description

Login, login, and login!

### Beginner Hint 1 (AI-translated)

- In `index.js`, a simple login feature is implemented.
- It appears to check that `users[username]` exists and that `users[username].password` matches the provided password.

- It doesn’t seem possible to create your own user. Also, a user called `admin` is registered, but guessing that password would be impossible.

### Beginner Hint 2 (AI-translated)

- In JavaScript, `users["foobar"]` and `users.foobar` are almost equivalent. Could this be used somehow?
- The login form alone might not allow you to send the intended data. For methods of sending data without using a browser, refer to [my writeup for I wanna be the Admin](https://github.com/tepel-chen/My-CTF-Challs/blob/main/Daily%20AlpacaHack/I%20wanna%20be%20the%20Admin/README.md).


## Writeup

### Overview

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

The goal of this challenge is to log in successfully. The only user that appears to exist is `admin`, but its password is impossible to predict.

### Solution

There are two checks: `user` must not be `undefined` or `null`, and `user.password` must match the provided password. Let's analyze them one by one.

In JavaScript, `users["admin"]` and `users.admin` are almost equivalent. Also, every object in JavaScript is an instance of `Object`, so its members and methods are accessible.

For example, `users.constructor` returns `Object`'s constructor function. This means `users["constructor"]` returns the same value. That value is neither `undefined` nor `null`, so setting `username="constructor"` passes the first check.

Bypassing the second check is simple: `user.password` is `undefined`, so we can pass by not sending `password` at all.

See [solver.py](./solution/solve.py) for the full exploit.

## Flag

`Alpaca{Javascr1pt_is_a_st4nge_languag3...}`
