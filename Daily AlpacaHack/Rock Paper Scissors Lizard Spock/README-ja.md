# Rock Paper Scissors Lizard Spock

[English](./README.md)

## 問題文

https://www.youtube.com/watch?v=jnfz_9d9BUA

## Writeup

### 概要

次の RPSLS ゲームで 100 連勝すると、フラグが取得できます。

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

RPSLS で 1 回勝つ確率は 40% なので、100 連勝できる確率はおよそ `1.6 x 10^-40` です。現実的な時間で解くには、何らかの方法で不正をする必要があります。

### 解法

この実装で気になるのは、**連勝数をサーバ側ではなく cookie に保存している**点です。

単に cookie を書き換えればよいと思うかもしれませんが、それはできません。サーバは **署名付き cookie** を使っているからです。値は次のようになっています。

```
s%3A1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro
```

URL デコードすると次のようになります。

```
s:1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro
```

`s:` は署名付きであることを示し、その後の `1` は連勝数が 1 であることを示します。続くランダムな文字列は **payload の HMAC** で、改ざんされていないことの検証に使われます。これを偽造するには `app.use(cookieParser(secret));` の secret が必要ですが、ここでは分かりません。

ただし、連勝数が 1 のときの署名付き cookie 値は常に `s:1.eP9t9XIB1Gb4gdQxg81EaA1q5iubh8Rc3EC3ENWQ0ro` です。つまり、負けて連勝数が 0 に戻っても、この値に cookie を戻せばサーバ側は受け入れてしまいます。

この操作を繰り返せば最終的に 100 連勝に到達し、フラグを取得できます。自動化方法は [solve.py](./solution/solve.py) を参照してください。

## フラグ

`Alpaca{And_as_it_always_has_Rock_crushes_Scissors}`
