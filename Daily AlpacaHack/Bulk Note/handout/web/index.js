import express from "express";
import { randomUUID } from "crypto";
import cookieParser from "cookie-parser";
import { load } from "js-yaml";

const FLAG = process.env.FLAG ?? "Alpaca{REDACTED}";

const app = express();
app.use(express.text({ type: "*/*" }));
app.use(cookieParser());

function sessionMiddleware(req, res, next) {
  let sessionId = req.cookies.sid;
  if (!sessionId) {
    sessionId = randomUUID();
    res.cookie("sid", sessionId);
  }
  req.sessionId = sessionId;
  next();
}

app.use(sessionMiddleware);

const notes = new Map();

function handleCreateCommand(doc, index, sessionId) {
  const content = doc.content;
  if (typeof content !== "string") {
    return [null, { error: "invalid content", index }];
  }

  const id = randomUUID();
  doc.sessionId = sessionId;
  if (doc.isHidden) {
    doc.content = FLAG;
    delete doc.sessionId;
    delete doc.isHidden;
  }
  notes.set(id, doc);

  return [
    {
      command: "create",
      id,
    },
    null,
  ];
}

function handleGetCommand(doc, index, sessionId) {
  const id = doc.id;
  if (typeof id !== "string") {
    return [null, { error: "invalid id", index }];
  }

  const note = notes.get(id);
  if (!note || !note.sessionId || note.sessionId !== sessionId) {
    return [null, { error: "not found", index }];
  }

  return [
    {
      command: "get",
      id,
      content: note.content,
    },
    null,
  ];
}

const commandHandlers = Object.create(null);
commandHandlers.create = handleCreateCommand;
commandHandlers.get = handleGetCommand;

app.get("/", (req, res) => {
  return res.type("html").send(`<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bulk Note</title>
</head>
<body>
  <textarea id="content1" rows="8" placeholder="content 1"></textarea>
  <label><input id="hidden1" type="checkbox">isHidden</label><br>
  <textarea id="content2" rows="8" placeholder="content 2"></textarea>
  <label><input id="hidden2" type="checkbox">isHidden</label><br>
  <textarea id="content3" rows="8" placeholder="content 3"></textarea>
  <label><input id="hidden3" type="checkbox">isHidden</label><br>
  <button id="submit">submit</button>
  <ul id="history"></ul>
  <pre id="output"></pre>

  <script src="https://cdn.jsdelivr.net/npm/js-yaml@4.1.1/dist/js-yaml.min.js"></script>
  <script>
    const rows = [
      { content: document.getElementById("content1"), hidden: document.getElementById("hidden1") },
      { content: document.getElementById("content2"), hidden: document.getElementById("hidden2") },
      { content: document.getElementById("content3"), hidden: document.getElementById("hidden3") },
    ];
    const submitBtn = document.getElementById("submit");
    const historyEl = document.getElementById("history");
    const outputEl = document.getElementById("output");

    async function runGet(id) {
      const payload = jsyaml.dump([{ command: "get", id }]);
      const resp = await fetch("/", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: payload,
      });
      const data = await resp.json();
      if (!resp.ok) {
        outputEl.textContent = "Error...";
        return;
      }

      const result = data.results && data.results[0];
      if (!result || typeof result.content !== "string") {
        outputEl.textContent = "Error...";
        return;
      }
      outputEl.textContent = result.content;
    }

    submitBtn.addEventListener("click", async () => {
      const docs = rows
        .map((row) => ({
          content: row.content.value,
          isHidden: row.hidden.checked,
        }))
        .filter((row) => row.content.length > 0)
        .map((row) => ({
          command: "create",
          content: row.content,
          isHidden: row.isHidden,
        }));

      try {
        const payload = jsyaml.dump(docs);
        const resp = await fetch("/", {
          method: "POST",
          headers: { "Content-Type": "text/plain" },
          body: payload,
        });
        const data = await resp.json();
        outputEl.textContent = resp.ok ? "Success!" : "Error...";

        if (!resp.ok || !Array.isArray(data.results)) {
          return;
        }

        for (const result of data.results) {
          if (!result || typeof result.id !== "string") {
            continue;
          }
          const li = document.createElement("li");
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = result.id;
          btn.addEventListener("click", async () => {
            try {
              await runGet(result.id);
            } catch (err) {
              outputEl.textContent = "Error...";
            }
          });
          li.appendChild(btn);
          historyEl.appendChild(li);
        }
      } catch (err) {
        outputEl.textContent = "Error...";
      }
    });
  </script>
</body>
</html>`);
});

app.post("/", (req, res) => {
  let parsedDocs;
  try {
    parsedDocs = load(req.body || "");
  } catch (err) {
    return res
      .status(400)
      .json({ error: "invalid yaml", detail: String(err.message || err) });
  }

  if (!Array.isArray(parsedDocs)) {
    return res.status(400).json({
      error: "invalid payload",
      detail: "top-level YAML must be an array",
    });
  }

  if (parsedDocs.length === 0) {
    return res.status(400).json({ error: "empty payload" });
  }

  const results = [];
  for (let i = 0; i < parsedDocs.length; i += 1) {
    const doc = parsedDocs[i];
    if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
      return res.status(400).json({ error: "invalid document", index: i });
    }

    const command = doc.command;
    if (
      typeof doc.command !== "string" ||
      !Object.hasOwn(commandHandlers, command)
    ) {
      return res
        .status(400)
        .json({ error: "unknown command", index: i, command });
    }
    const handler = commandHandlers[command];
    const [result, error] = handler(doc, i, req.sessionId);
    if (error) {
      return res.status(400).json(error);
    }
    results.push(result);
  }

  return res.status(200).json({ results });
});

const port = Number(process.env.PORT || 3000);
app.listen(port, "0.0.0.0");
