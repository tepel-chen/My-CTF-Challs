import express from "express";
import rateLimit from "express-rate-limit";
import { visit, APP_URL } from "./bot.js";

const app = express();
app.use(express.json());
app.set("view engine", "ejs");

app.get("/", async (_req, res) => {
  return res.render("./index.ejs", { APP_URL });
});

// Limit each IP address to 3 requests per minute
app.use("/api", rateLimit({ windowMs: 60 * 1000, max: 3 }));

app.post("/api/report", async (req, res) => {
  try {
    const result = await visit(APP_URL);
    return res.send(result);
  } catch (e) {
    console.error(e);
    return res.status(500).send("Something wrong");
  }
});

app.listen(1337, () => {
  console.log('Server listening on port 1337');
});
