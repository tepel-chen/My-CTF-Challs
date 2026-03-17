import express from "express";
import cookieParser from "cookie-parser";
import crypto from "crypto";

const FLAG = process.env.FLAG ?? "Alpaca{fake_flag}";

const app = express();
const secret = crypto.randomUUID();

app.use(express.urlencoded({ extended: false }));
app.use(cookieParser(secret));

const valid_inputs = ["rock", "paper", "scissors", "lizard", "spock"];
const winsAgainst = {
  rock: ["scissors", "lizard"],
  paper: ["rock", "spock"],
  scissors: ["paper", "lizard"],
  lizard: ["spock", "paper"],
  spock: ["scissors", "rock"],
};

app.get("/", async (req, res) => {
  const rawStreak = req.signedCookies.streak ?? "0";
  const parsedStreak = Number.parseInt(rawStreak, 10);
  const streak = Number.isNaN(parsedStreak) ? 0 : parsedStreak;
  const flash = req.signedCookies.flash;

  if (flash) {
    res.clearCookie("flash", { signed: true });
  }

  const buttons = valid_inputs
    .map(
      (choice) =>
        `<button type="submit" name="input" value="${choice}">${choice}</button>`
    )
    .join("");

  return res.send(`<!DOCTYPE html>
<html>
<body>
  ${flash ? `<p>${flash}</p>` : ""}
  <p>Current streak: ${streak}</p>
  <form method="POST" action="/rpsls">
    ${buttons}
  </form>
  ${streak >= 100 ? FLAG : "Win 100 times in a row to get the flag!"}
</body>
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

app.listen(3000, () => {
  console.log(`Listening on http://localhost:3000`);
});
