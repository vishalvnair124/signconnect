from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

# OpenCV: capture video from webcam (0 = default cam)
camera = cv2.VideoCapture(0)

# Function to generate frames
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield frame for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Simple HTML page with video stream
    return render_template_string("""
        <html>
            <head>
                <title>Video Stream</title>
            </head>
            <body>
                <h2>Live Video Stream</h2>
                <img src="{{ url_for('video_feed') }}" width="640" height="480">
            </body>
        </html>
    """)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
