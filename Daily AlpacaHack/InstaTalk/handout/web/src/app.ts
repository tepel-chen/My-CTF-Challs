import express from "express";
import path from "path";
import { randomUUID } from "crypto";
import type { UUID } from "crypto";
import cookieParser from "cookie-parser";
import DOMPurify from "isomorphic-dompurify";

const app = express();

app.use(express.json());
app.use(cookieParser(randomUUID()));

function createMessage(message: string, from: UUID, to: UUID) {
  const payload: string = DOMPurify.sanitize(
    `<li><p>${from.slice(0, 8)} → ${to.slice(0, 8)}</p><p>${message}</p></li>`.replaceAll("\n", ""),
  );
  if(payload.includes("\n")) {
    return `event: message\ndata: [Deleted for security reason.]\n\n`;
  }
  return `event: message\ndata: ${payload}\n\n`;
}

function isUUID(value: unknown): value is UUID {
  return (
    typeof value === "string" &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      value,
    )
  );
}

app.get("/", (req: express.Request, res: express.Response) => {
  let uuid = req.signedCookies.uuid;
  if (!uuid) {
    uuid = randomUUID();
    res.cookie("uuid", uuid, { httpOnly: true, signed: true });
  }

  res.sendFile(path.join(import.meta.dirname, "index.html"));
});

let clients: Map<UUID, express.Response> = new Map();

app.get("/api/events", (req: express.Request, res: express.Response) => {
  let uuid = req.signedCookies.uuid;
  if (!isUUID(uuid)) {
    res.status(400).json({ error: "Missing cookie" });
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders();

  clients.set(uuid, res);

  res.write(`event: start\n`);
  res.write(`data: ${uuid}\n\n`);

  req.on("close", () => {
    clients.delete(uuid);
  });
});

app.post("/api/send-message", (req: express.Request, res: express.Response) => {
  const { message, to } = req.body;

  if (!isUUID(to)) {
    res.status(400).json({ error: "Missing to parameter" });
    return;
  }

  const from = req.signedCookies.uuid;
  if (!isUUID(from)) {
    res.status(400).json({ error: "Missing cookie" });
    return;
  }

  const toClient = clients.get(to);
  const fromClient = clients.get(from);

  if (!toClient || !fromClient) {
    res.status(404).json({ error: "Client not found" });
    return;
  }

  toClient.write(createMessage(message, from, to));
  fromClient.write(createMessage(message, from, to));

  res.status(200).send("Message sent");
});

app.listen(3000, () => {
  console.log(`Server is running on http://localhost:3000`);
});
