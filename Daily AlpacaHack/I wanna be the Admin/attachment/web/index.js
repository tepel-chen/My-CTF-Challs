const express = require("express");
const cookieParser = require("cookie-parser");

const FLAG = process.env.FLAG ?? "Alpaca{REDACTED}";

const app = express();
app.use(cookieParser());
app.use(express.urlencoded({ extended: false }));

let users = new Map();

setInterval(() => {
  users.clear();
  console.log("[RESET] all users cleared");
}, 10 * 60 * 1000);

function auth(req, res, next) {
  const username = req.cookies.username;
  if (!username) return res.redirect("/login");

  const user = users.get(username);
  if (!user) return res.redirect("/login");

  req.user = user;
  next();
}

app.get("/register", (req, res) => {
  res.send(`
    <h2>Register</h2>
    <form method="POST">
      <input name="username" placeholder="username" required />
      <br />
      <input name="password" type="password" placeholder="password" required />
      <br />
      <input name="nickname" placeholder="nickname" />
      <br />
      <button>Register</button>
    </form>
    <a href="/login">Login</a>
  `);
});

app.post("/register", (req, res) => {
  const user_data = req.body;
  if (
    !user_data ||
    !user_data.username ||
    !user_data.password ||
    !/^[a-z0-9]+$/.test(user_data.username) ||
    (user_data.nickname && !/^[a-z0-9]+$/.test(user_data.nickname))
  )
    return res.send("invalid input");

  if (users.has(user_data.username)) {
    return res.send("user already exists");
  }

  users.set(user_data.username, {
    role: "guest",
    ...user_data,
  });

  res.cookie("username", user_data.username);
  res.redirect("/");
});

app.get("/login", (req, res) => {
  res.send(`
    <h2>Login</h2>
    <form method="POST">
      <input name="username" placeholder="username" required />
      <br />
      <input name="password" type="password" placeholder="password" required />
      <br />
      <button>Login</button>
    </form>
    <a href="/register">Register</a>
  `);
});

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  const user = users.get(username);
  if (!user || user.password !== password) {
    return res.send("invalid credentials");
  }

  res.cookie("username", username);
  res.redirect("/");
});

app.get("/", auth, (req, res) => {
  const { username, role, nickname } = req.user;

  res.send(`
    <h1>Hello ${username} (${nickname ?? "no nickname"})</h1>
    <p>role: ${role}</p>
    ${role === "admin" ? `<p><b>${FLAG}</b></p>` : ""}
    <a href="/logout">Logout</a>
  `);
});

app.get("/logout", (req, res) => {
  res.clearCookie("username");
  res.redirect("/login");
});

app.listen(3000, () => {
  console.log("http://localhost:3000");
});
