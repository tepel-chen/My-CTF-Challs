import { ServerRouter } from "https://deno.land/x/server_router@v1.2.0/mod.ts";

const router = new ServerRouter();
const flag = Deno.env.get("FLAG") || "ictf{fake_flag}"

router
  .caseSensitive()
  .route("/", (_req) => new Response("hello"))
  .route("/flag", (_req) => new Response(flag));

await Deno.serve({ port: 4002 }, router.handler);