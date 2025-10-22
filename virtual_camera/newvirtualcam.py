import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import datetime
import threading
import speech_recognition as sr
import json
import os
from collections import deque

# ------------------- Load sign dictionary -------------------
with open("sign_dict.json", "r") as f:
    sign_dict = json.load(f)

VIDEO_PATH = r"D:\signcsv"  # folder where videos are stored

# ------------------- Speech Recognition -------------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

recognized_text = ""
video_queue = deque()  # queue of video file paths
current_video = None
video_cap = None

def listen_microphone():
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

                # Split into words/phrases
                words = text.split()
                for word in words:
                    if word in sign_dict:
                        video_file = os.path.join(VIDEO_PATH, f"{word}.mp4")
                        if os.path.exists(video_file):
                            video_queue.append(video_file)
                            print(f"Queued video for '{word}'")

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("API unavailable:", e)
                break

threading.Thread(target=listen_microphone, daemon=True).start()

# ------------------- Webcam + Virtual Cam -------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30

print(f"Webcam opened: {width}x{height} @ {fps}fps")

with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR) as cam:
    print(f'Virtual camera device: {cam.device}')
    print("Streaming... Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror
        frame = cv2.flip(frame, 1)

        # Timestamp
        cv2.putText(frame,
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)

        # Voice text overlay
        if recognized_text:
            cv2.putText(frame,
                        recognized_text,
                        (20, height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2)

        # Handle video playback queue
        if video_cap is None and video_queue:
            # load next video
            current_video = video_queue.popleft()
            video_cap = cv2.VideoCapture(current_video)
            print(f"Playing: {current_video}")

        if video_cap is not None and video_cap.isOpened():
            ret2, vid_frame = video_cap.read()
            if ret2:
                # Bigger overlay (e.g., 400x400)
                vid_frame = cv2.resize(vid_frame, (400, 400))
                x_offset = width - 410
                y_offset = 10
                frame[y_offset:y_offset+400, x_offset:x_offset+400] = vid_frame
            else:
                video_cap.release()
                video_cap = None

        # Send to virtual camera
        cam.send(frame)
        cam.sleep_until_next_frame()

cap.release()
cv2.destroyAllWindows()
