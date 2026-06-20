import { randomUUID } from "crypto";
import { join } from "path";
import cookieParser from "cookie-parser";
import DOMPurify from "isomorphic-dompurify";
import express, { urlencoded } from "express";

const app = express();
const port = Number(process.env.PORT || 3000);
const todosBySession = new Map();

app.set("view engine", "ejs");
app.set("views", join(import.meta.dirname, "views"));

app.use(cookieParser());
app.use(urlencoded({ extended: false }));

function sessionIdMiddleware(req, res, next) {
  let sessionId = req.cookies.sessionId;

  if (!sessionId) {
    sessionId = randomUUID();
    res.cookie("sessionId", sessionId, {
      httpOnly: true,
      sameSite: "lax"
    });
  }

  req.sessionId = sessionId;
  next();
}

app.use(sessionIdMiddleware);

app.get("/", async (req, res) => {
  const targetSessionId = String(req.query.sessionId || "").trim() || req.sessionId;
  const isReadonly = targetSessionId !== req.sessionId;
  const todos = todosBySession.get(targetSessionId) || [];
  res.render("index", {
    todos,
    pageTitle: isReadonly ? "TODO List (Readonly)" : "TODO List",
    activeSessionId: targetSessionId,
    isReadonly
  });
});

app.post("/todos", async (req, res) => {
  const rawTitle = String(req.body.title || "").trim().slice(0, 255);
  const title = DOMPurify.sanitize(rawTitle).slice(0, 255);

  if (title) {
    const todos = todosBySession.get(req.sessionId) || [];
    todosBySession.set(req.sessionId, [title, ...todos]);
  }

  res.redirect("/");
});

app.listen(port, async () => {
  console.log(`Listening on port ${port}`);
});
