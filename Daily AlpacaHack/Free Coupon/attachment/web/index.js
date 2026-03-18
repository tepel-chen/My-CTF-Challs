import express from "express";
import cookieParser from "cookie-parser";
import crypto from "crypto";

const FLAG = process.env.FLAG ?? "Alpaca{fake_flag}";

const app = express();

app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

const sessions = new Map();

function session(req, res, next) {
  let sid = req.cookies.sid;
  if (!sid || !sessions.has(sid)) {
    sid = crypto.randomUUID();
    sessions.set(sid, {
      redeemed: false,
      balance: 0,
    });
    res.cookie("sid", sid);
  }
  req.sid = sid;
  next();
}

app.get("/", session, async (req, res) => {
  const { redeemed, balance } = sessions.get(req.sid);

  return res.send(`<!DOCTYPE html>
<html>
<body>
  <p>Your balance: ${balance}<p>
  ${balance >= 30 ? '<a href="/buy">Buy a flag</a>' : "You don't have enough money to buy a flag"}<br>
  ${redeemed ? "You already redeemed your coupon." : '<a href="/redeem">Redeem your coupon</a>'}<br>
</body>
</html>`);
});

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

app.get("/buy", session, async (req, res) => {
  const sessionData = sessions.get(req.sid);

  if (sessionData.balance >= 30) {
    sessions.set(req.sid, {
      ...sessionData,
      balance: sessionData.balance - 30,
    });
    return res.send(FLAG);
  }
  return res.send(
    `You don't have enough money to buy the flag. <a href="/">Home</a>`,
  );
});

app.listen(3000, () => {
  console.log(`Listening on http://localhost:3000`);
});
