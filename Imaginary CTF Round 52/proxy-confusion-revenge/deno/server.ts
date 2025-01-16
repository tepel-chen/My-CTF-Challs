import { ServerRouter } from "https://deno.land/x/server_router@v1.2.0/mod.ts";

const router = new ServerRouter();
const flag = Deno.env.get("FLAG") || "ictf{fake_flag}"

router
  .caseSensitive()
  .route("/", (_req) => new Response("hello"))
  .route("/flag", async (_req) => {
    if(_req.method !== "POST" || (await _req.text()).trim() !== "please give me flag") {
      return new Response("Hacker!", {
        headers: {
          Connection: "close"
        }
      })
    }
    return new Response(flag, {
      headers: {
        Connection: "close"
      }
    })
  });

Deno.serve({ port: 4002 }, router.handler);