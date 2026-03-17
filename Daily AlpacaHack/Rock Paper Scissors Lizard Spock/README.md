# Rock Paper Scissors Lizard Spock

[日本語版はこちら](./README-ja.md)

## Description

https://www.youtube.com/watch?v=jnfz_9d9BUA

## Writeup

### Overview

If you can beat the following RPSLS game 100 times in a row, you will get the flag.

```javascript
app.get("/", async (req, res) => {
  /* ... */
  const parsedStreak = Number.parseInt(rawStreak, 10);
  const streak = Number.isNaN(parsedStreak) ? 0 : parsedStreak;
  /* ... */

  return res.send(`<!DOCTYPE html>
    ...
  ${streak >= 100 ? FLAG : "Win 100 times in a row to get the flag!"}
    ...
</html>`);
});

app.post("/rpsls", async (req, res) => {
  const { input } = req.body;
  if(!valid_inputs.includes(input)) {
    res.cookie("streak", "0", { signed: true });
    res.cookie("flash", "Invalid input", { signed: true });
    return res.redirect("/");
  }

  const opponent = valid_inputs[Math.floor(crypto.randomInt(valid_inputs.length))];
  const currentStreakRaw = req.signedCookies.streak ?? "0";
  const currentStreakParsed = Number.parseInt(currentStreakRaw, 10);
  const currentStreak = Number.isNaN(currentStreakParsed) ? 0 : currentStreakParsed;

  if (input === opponent) {
    res.cookie("streak", "0", { signed: true });
    res.cookie("flash", "Draw!", { signed: true });
  } else if (winsAgainst[input].includes(opponent)) {
    const nextStreak = currentStreak + 1;
    res.cookie("streak", String(nextStreak), { signed: true });
    res.cookie("flash", `You beat ${opponent}!`, { signed: true });
  } else {
    res.cookie("streak", "0", { signed: true });
    res.cookie("flash", `You lost! ${opponent} beats ${input}.`, { signed: true });
  }

  return res.redirect("/");
});
```

Your chance of winning a single RPSLS round is 40%, so winning 100 rounds in a row is about `1.6 x 10^-40`. To solve this challenge in a reasonable amount of time, you need to cheat somehow.

### Solution

An interesting part of this implementation is that **it stores the streak in your cookie** instead of storing it on the server.

You might think that you can simply overwrite the cookie, but that is not possible. This is because the server uses a **signed cookie**. It looks like this:

```
s%3A1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro
```

After URL decoding, it looks like this:

```
s:1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro
```

`s:` means the value is signed, and the following `1` means the streak is 1. The random-looking string that follows is the **HMAC of the payload**, which verifies that the content was not forged. To forge this, you would need the secret used in `app.use(cookieParser(secret));`, which we do not know.

However, the signed cookie value is always the same when your streak is 1: `s:1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro`. This means that if you lose and your streak is reset to 0, you can restore the cookie to that value, and the server will accept it.

By repeating this process, you can eventually reach a streak of 100 and get the flag. See [solve.py](./solution/solve.py) for an automated approach.


## Flag

`Alpaca{And_as_it_always_has_Rock_crushes_Scissors}`
