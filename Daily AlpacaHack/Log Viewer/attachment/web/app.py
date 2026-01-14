import subprocess
from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    log = ""
    if request.method == "POST":
        query = request.form.get("query", "")

        command = ["awk", f"/{query}/", "info.log"]
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=1,
            text=True,
        )
        log = result.stderr or result.stdout
    
    return render_template(
        "index.html",
        log=log,
        query=query,
    )
