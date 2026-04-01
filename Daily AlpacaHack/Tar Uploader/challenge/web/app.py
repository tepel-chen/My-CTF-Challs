import shutil
from pathlib import Path
from uuid import uuid4
from tarfile import TarFile

from flask import Flask, render_template, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 # 1MB

STATIC_ROOT = Path(app.static_folder)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename == "":
        return render_template("index.html", error="Tar file is required"), 400

    upload_id = str(uuid4())
    destination = STATIC_ROOT / upload_id
    destination.mkdir(parents=True, exist_ok=False)

    try:
        with TarFile(fileobj=uploaded_file) as archive:
            archive.extractall(str(destination))
    except Exception as e:
        shutil.rmtree(destination, ignore_errors=True)
        return render_template("index.html", error="Invalid tar file"), 400

    return render_template("index.html", success=f"Successfully uploaded to {upload_id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
