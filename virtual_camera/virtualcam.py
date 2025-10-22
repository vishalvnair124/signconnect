import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import datetime
import threading
import speech_recognition as sr

# ------------------- Speech Recognition Setup -------------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

recognized_text = ""  # global variable to store latest recognized text

def listen_microphone():
    global recognized_text
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for voice input...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio)  # you can swap with other engines
                recognized_text = text
                print("Recognized:", text)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("API unavailable:", e)
                break

# Start voice recognition in a background thread
threading.Thread(target=listen_microphone, daemon=True).start()

# ------------------- Video Capture Setup -------------------
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

    grayscale = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror image
        frame = cv2.flip(frame, 1)

        # Key controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('g'):
            grayscale = not grayscale
        elif key == ord('q'):
            break

        # Apply grayscale if toggled
        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Add timestamp overlay
        cv2.putText(frame,
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)

        # Add live voice-to-text overlay
        if recognized_text:
            cv2.putText(frame,
                        recognized_text,
                        (20, height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2)

        # Send frame to virtual webcam
        cam.send(frame)
        cam.sleep_until_next_frame()

cap.release()
cv2.destroyAllWindows()
