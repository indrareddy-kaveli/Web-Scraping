import os
from flask import Flask, jsonify, send_from_directory

from main import run_pipeline

app = Flask(__name__, static_folder=".", static_url_path="")


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/run")
def run_job():
    result = run_pipeline()
    return jsonify({"status": "completed", "summary": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
