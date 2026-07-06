import express from "express";
import rateLimit from "express-rate-limit";
import { visit, APP_URL } from "./bot.js";

const app = express();
app.use(express.json());
app.set("view engine", "ejs");

app.get("/", async (_req, res) => {
  return res.render("./index.ejs", { APP_URL });
});

// Limit each IP address to 4 requests per minute
app.use("/api", rateLimit({ windowMs: 60 * 1000, max: 4 }));

app.post("/api/report", async (req, res) => {
  const { path } = req.body;
  if (typeof path !== "string") {
    return res.status(400).send("Invalid path");
  }
  const url = APP_URL + path;

  try {
    await visit(url);
    return res.send("OK");
  } catch (e) {
    console.error(e);
    return res.status(500).send("Something wrong");
  }
});

app.listen(1337, () => {
  console.log('Server listening on port 1337');
});
