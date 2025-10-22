import cv2
import pandas as pd
import numpy as np
import mediapipe as mp

# === MediaPipe landmark connections ===
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

FACE_CONNECTIONS = mp_face_mesh.FACEMESH_TESSELATION
HAND_CONNECTIONS = mp_hands.HAND_CONNECTIONS
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# === Load CSV landmarks ===
df = pd.read_csv("howareyou.csv")

# Clean & convert columns
for col in ['frame', 'index', 'hand_index', 'x', 'y', 'z']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df.dropna(inplace=True)
df = df.sort_values(by='frame')
df['frame'] = df['frame'].astype(int)
df['index'] = df['index'].astype(int)
df['hand_index'] = df['hand_index'].astype(int)

# === Display parameters ===
FRAME_W, FRAME_H = 1200, 700
SCALE_FACTOR = 1  # zoom in a bit

n_frames = df['frame'].max()
print(f"🎞️ Total frames: {n_frames}")

# === Utility: Draw landmarks & connections ===
def draw_landmarks(image, part_data, connections, color, center_x, center_y):
    if part_data.empty:
        return

    points = {}
    for _, row in part_data.iterrows():
        x = row['x'] * FRAME_W
        y = row['y'] * FRAME_H
        x = center_x + (x - center_x) * SCALE_FACTOR
        y = center_y + (y - center_y) * SCALE_FACTOR
        points[row['index']] = (int(x), int(y))

    # Draw dots
    for pt in points.values():
        cv2.circle(image, pt, 2, color, -1)

    # Draw lines
    for start, end in connections:
        if start in points and end in points:
            cv2.line(image, points[start], points[end], color, 1)

# === Playback loop ===
for frame_idx in range(1, n_frames + 1):
    canvas = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)

    # Data for current frame
    frame_data = df[df['frame'] == frame_idx]

    # Compute center of all landmarks (for scaling around center)
    cx = (frame_data['x'] * FRAME_W).mean()
    cy = (frame_data['y'] * FRAME_H).mean()

    # Draw face
    face_data = frame_data[frame_data['part'] == 'face']
    draw_landmarks(canvas, face_data, FACE_CONNECTIONS, (0, 255, 0), cx, cy)

    # Draw both hands
    for hand_idx, color in zip([0, 1], [(255, 0, 0), (0, 165, 255)]):
        hand_data = frame_data[(frame_data['part'] == 'hand') & (frame_data['hand_index'] == hand_idx)]
        draw_landmarks(canvas, hand_data, HAND_CONNECTIONS, color, cx, cy)

    # Draw pose
    pose_data = frame_data[frame_data['part'] == 'pose']
    draw_landmarks(canvas, pose_data, POSE_CONNECTIONS, (128, 0, 128), cx, cy)

    # Show frame
    cv2.imshow("Landmark Playback", canvas)
    if cv2.waitKey(30) & 0xFF == 27:
        break

cv2.destroyAllWindows()
