import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import datetime
import threading
import speech_recognition as sr
import json
import requests
import tempfile
import os
from collections import deque

# ------------------- Config -------------------
SERVER_URL = "http://localhost:5000/video"  # Flask server base
with open("sign_dict.json", "r") as f:
    sign_dict = json.load(f)

# Path to default video (must exist in same directory as script)
DEFAULT_VIDEO_PATH = os.path.join(os.getcwd(), "default.mp4")

# ------------------- Overlay Helper -------------------
def overlay_on_frame(base_frame, overlay_frame, x, y):
    """Safely overlay overlay_frame onto base_frame at (x,y)"""
    h, w, _ = overlay_frame.shape
    H, W, _ = base_frame.shape

    # Clip overlay if it goes out of bounds
    if x + w > W:
        w = W - x
        overlay_frame = overlay_frame[:, :w]
    if y + h > H:
        h = H - y
        overlay_frame = overlay_frame[:h, :]

    if h > 0 and w > 0:
        base_frame[y:y+h, x:x+w] = overlay_frame
    return base_frame

# ------------------- Speech Recognition -------------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

recognized_text = ""
video_queue = deque()  # queue of local temp video paths
video_cap = None
default_cap = cv2.VideoCapture(DEFAULT_VIDEO_PATH)  # Default video capture

def download_video(word):
    """Fetch video from Flask server and save to temp file"""
    url = f"{SERVER_URL}/{word}.mp4"
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
            with os.fdopen(tmp_fd, "wb") as tmp_file:
                for chunk in response.iter_content(1024*1024):
                    tmp_file.write(chunk)
            return tmp_path
        else:
            print(f"Video not found for {word}")
            return None
    except Exception as e:
        print(f"Error fetching {word}: {e}")
        return None

def listen_microphone():
    """Continuously listen for microphone input and queue matching videos"""
    global recognized_text, video_queue
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for voice input...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                recognized_text = text
                print("Recognized:", text)

                for word in text.split():
                    if word in sign_dict:
                        tmp_path = download_video(word)
                        if tmp_path:
                            video_queue.append(tmp_path)
                            print(f"Queued video for '{word}'")

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("API unavailable:", e)
                break

# Run speech recognition in background
threading.Thread(target=listen_microphone, daemon=True).start()

# ------------------- Webcam + Virtual Cam -------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# ================== RESOLUTION SETTINGS ==================
DESIRED_WIDTH = 1280
DESIRED_HEIGHT = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, DESIRED_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DESIRED_HEIGHT)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30

print(f"Webcam opened: {width}x{height} @ {fps}fps")
# ========================================================

# Initialize virtual camera
with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR) as cam:
    print(f'Virtual camera device: {cam.device}')
    print("Streaming... Press Ctrl+C to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --------- Timestamp overlay ---------
        # cv2.putText(frame,
        #             datetime.datetime.now().strftime("%H:%M:%S"),
        #             (20, 50),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             1,
        #             (0, 255, 0),
        #             2)

        # --------- Voice text overlay ---------
        # if recognized_text:
        #     cv2.putText(frame,
        #                 recognized_text,
        #                 (20, height - 50),
        #                 cv2.FONT_HERSHEY_SIMPLEX,
        #                 1,
        #                 (255, 255, 255),
        #                 2)

        # --------- Handle video overlays ---------
        if video_cap is None and video_queue:
            # Load next queued video
            current_video = video_queue.popleft()
            video_cap = cv2.VideoCapture(current_video)
            print(f"Playing: {current_video}")

        # Play queued video if available
        if video_cap is not None and video_cap.isOpened():
            ret2, vid_frame = video_cap.read()
            if ret2:
                overlay_h = height // 3
                overlay_w = width // 3
                vid_frame = cv2.resize(vid_frame, (overlay_w, overlay_h))
                x_offset = width - overlay_w - 10
                y_offset = 10
                frame = overlay_on_frame(frame, vid_frame, x_offset, y_offset)
            else:
                video_cap.release()
                video_cap = None

        # If no queued video, always play default.mp4
        if video_cap is None:
            if not default_cap.isOpened():
                default_cap = cv2.VideoCapture(DEFAULT_VIDEO_PATH)
            ret3, def_frame = default_cap.read()
            if not ret3:
                # Restart default video loop
                default_cap.release()
                default_cap = cv2.VideoCapture(DEFAULT_VIDEO_PATH)
                ret3, def_frame = default_cap.read()
            if ret3:
                overlay_h = height // 3
                overlay_w = width // 3
                def_frame = cv2.resize(def_frame, (overlay_w, overlay_h))
                x_offset = width - overlay_w - 10
                y_offset = 10
                frame = overlay_on_frame(frame, def_frame, x_offset, y_offset)

        # --------- Send to virtual camera ---------
        cam.send(frame)
        cam.sleep_until_next_frame()

# Cleanup
cap.release()
cv2.destroyAllWindows()
