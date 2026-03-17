import express, { urlencoded } from "express";
import crypto from "crypto";

const FLAG = process.env.FLAG ?? "Alpaca{REDACTED}";

const app = express();
app.use(urlencoded({ extended: false }));

let users = {
  admin: {
    password: crypto.randomBytes(32).toString("base64"),
  },
};

app.get("/", (req, res) => {
  res.send(`
    <h2>Login</h2>
    <form method="POST">
      <input name="username" placeholder="username" required />
      <br />
      <input name="password" type="password" placeholder="password" required />
      <br />
      <button>Login</button>
    </form>
  `);
});

app.post("/", (req, res) => {
  const { username, password } = req.body;
  const user = users[username];
  if (!user || user.password !== password) {
    return res.send("invalid credentials");
  }

  res.send(FLAG);
});

app.listen(3000, () => {
  console.log("http://localhost:3000");
});
