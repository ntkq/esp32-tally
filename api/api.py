from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CERT_FILE = BASE_DIR / "cert.pem"
KEY_FILE = BASE_DIR / "key.pem"

last_upload = {"timestamp": None, "completed": False}
metrics = PrometheusMetrics(app)

@app.route("/", methods=["GET", "POST"])
def esp32_api():
    global last_upload
    if request.method == "POST":
        data = request.get_json() or {}
        completed = data.get("complete", False)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        last_upload = {"timestamp": timestamp, "completed": completed}

        print(f"got data: {last_upload}")
        return jsonify({"status": "success", "last_time": timestamp}), 200

    return (
        jsonify(
            {
                "status": "online",
                "message": "api is running",
                "last_upload": last_upload,
            }
        ),
        200,
    )


if __name__ == "__main__":
    # using HTTP instead of HTTPS for initial demo
    #if CERT_FILE.exists() and KEY_FILE.exists():
        #app.run(ssl_context=(CERT_FILE, KEY_FILE), host="0.0.0.0", port=8443)
    #else:
    #    app.run(host="0.0.0.0", port=5000) 
    app.run(host="0.0.0.0", port=5000)
