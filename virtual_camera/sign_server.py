from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

# Path where your sign videos are stored
VIDEO_FOLDER = r"D:\coding_projects\python_projects\sign_connect\sign_animation"

@app.route("/video/<path:filename>")
def get_video(filename):
    file_path = os.path.join(VIDEO_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(VIDEO_FOLDER, filename)
    else:
        abort(404, "Video not found")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
