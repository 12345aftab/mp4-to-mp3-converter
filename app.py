from flask import Flask, request, send_file, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Website
@app.route("/")
def home():
    index_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "index.html"
    )

    if not os.path.exists(index_path):
        return "index.html not found", 404

    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


# MP4 to MP3
@app.route("/convert", methods=["POST"])
def convert():

    if "file" not in request.files:
        return jsonify({"error": "No file received"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".mp4"):
        return jsonify({"error": "Only MP4 files are allowed"}), 400

    quality = request.form.get("quality", "192")

    if quality not in ["128", "192", "256", "320"]:
        quality = "192"

    file_id = str(uuid.uuid4())

    input_file = os.path.join(
        UPLOAD_FOLDER,
        file_id + ".mp4"
    )

    output_file = os.path.join(
        OUTPUT_FOLDER,
        file_id + ".mp3"
    )

    file.save(input_file)

    try:

        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file,
                "-vn",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                quality + "k",
                "-y",
                output_file
            ],
            check=True
        )

        return send_file(
            output_file,
            as_attachment=True,
            download_name="converted.mp3",
            mimetype="audio/mpeg"
        )

    except Exception as error:

        return jsonify({
            "error": "Conversion failed",
            "details": str(error)
        }), 500

    finally:

        if os.path.exists(input_file):
            os.remove(input_file)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )