import cv2
import pandas as pd
import numpy as np
import mediapipe as mp
import os
from pathlib import Path

# === MediaPipe landmark connections ===
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

FACE_CONNECTIONS = mp_face_mesh.FACEMESH_TESSELATION
HAND_CONNECTIONS = mp_hands.HAND_CONNECTIONS
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# === Display parameters ===
FRAME_W, FRAME_H = 1200, 700
SCALE_FACTOR = 1
FPS = 30   # frames per second of output video

# === Color variables (BGR) ===
BACKGROUND_COLOR = (255, 255, 255)    # White background
FACE_COLOR = (0, 255, 0)              # Green
LEFT_HAND_COLOR = (255, 0, 0)         # Blue
RIGHT_HAND_COLOR = (0, 165, 255)      # Orange
POSE_COLOR = (128, 0, 128)            # Purple

# === Paths ===
input_folder = Path(r"D:\signcsv")
output_folder = Path(r"D:\sign_animation")
output_folder.mkdir(exist_ok=True)

# === Utility: Draw landmarks ===
def draw_landmarks(image, part_data, connections, color, center_x, center_y,
                   point_size=5, line_thickness=2):
    if part_data.empty:
        return

    points = {}
    for _, row in part_data.iterrows():
        x = row['x'] * FRAME_W
        y = row['y'] * FRAME_H
        x = center_x + (x - center_x) * SCALE_FACTOR
        y = center_y + (y - center_y) * SCALE_FACTOR
        points[row['index']] = (int(x), int(y))

    for pt in points.values():
        cv2.circle(image, pt, point_size, color, -1)

    for start, end in connections:
        if start in points and end in points:
            cv2.line(image, points[start], points[end], color, line_thickness)

# === Process each CSV file ===
for csv_file in input_folder.glob("*.csv"):
    print(f"Processing {csv_file.name}...")

    # Load CSV
    df = pd.read_csv(csv_file)
    for col in ['frame', 'index', 'hand_index', 'x', 'y', 'z']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)
    df = df.sort_values(by='frame')
    df['frame'] = df['frame'].astype(int)
    df['index'] = df['index'].astype(int)
    df['hand_index'] = df['hand_index'].astype(int)

    n_frames = df['frame'].max()
    print(f"  Total frames: {n_frames}")

    # === Prepare video writer ===
    out_path = output_folder / f"{csv_file.stem}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec
    writer = cv2.VideoWriter(str(out_path), fourcc, FPS, (FRAME_W, FRAME_H))

    # === Playback & write ===
    for frame_idx in range(1, n_frames + 1):
        canvas = np.full((FRAME_H, FRAME_W, 3), BACKGROUND_COLOR, dtype=np.uint8)
        frame_data = df[df['frame'] == frame_idx]

        cx = (frame_data['x'] * FRAME_W).mean()
        cy = (frame_data['y'] * FRAME_H).mean()

        # Face
        face_data = frame_data[frame_data['part'] == 'face']
        draw_landmarks(canvas, face_data, FACE_CONNECTIONS, FACE_COLOR, cx, cy, point_size=3, line_thickness=1)

        # Hands
        for hand_idx, color in zip([0, 1], [LEFT_HAND_COLOR, RIGHT_HAND_COLOR]):
            hand_data = frame_data[(frame_data['part'] == 'hand') & (frame_data['hand_index'] == hand_idx)]
            draw_landmarks(canvas, hand_data, HAND_CONNECTIONS, color, cx, cy, point_size=3, line_thickness=2)

        # Pose
        pose_data = frame_data[frame_data['part'] == 'pose']
        draw_landmarks(canvas, pose_data, POSE_CONNECTIONS, POSE_COLOR, cx, cy, point_size=4, line_thickness=2)

        writer.write(canvas)  # save frame to video

    writer.release()
    print(f"  ✅ Saved: {out_path}")

print("🎉 All CSV files processed into videos.")
