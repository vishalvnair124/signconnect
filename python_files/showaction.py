import cv2
import pandas as pd
import numpy as np
import mediapipe as mp

# MediaPipe connections
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

face_connections = mp_face_mesh.FACEMESH_TESSELATION
hand_connections = mp_hands.HAND_CONNECTIONS
pose_connections = mp_pose.POSE_CONNECTIONS

# Load and clean CSV
df = pd.read_csv("D:/signcsv/today.csv",)

# Make numeric & drop bad rows
for col in ['frame', 'index', 'hand_index', 'x', 'y', 'z']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()
df = df.sort_values(by='frame')
df['frame'] = df['frame'].astype(int)
df['index'] = df['index'].astype(int)
df['hand_index'] = df['hand_index'].astype(int)

# Frame properties
w, h = 1200,700 
n_frames = df['frame'].max()
print(f"Total frames: {n_frames}")

scale_factor = 1  # slightly less aggressive scaling

for frame_idx in range(1, n_frames + 1):
    img = np.zeros((h, w, 3), dtype=np.uint8)

    frame_data = df[df['frame'] == frame_idx]

    all_xs = frame_data['x'] * w
    all_ys = frame_data['y'] * h
    cx, cy = np.mean(all_xs), np.mean(all_ys)

    # Function to process each part
    def draw_part(part_data, connections, color):
        if part_data.empty:
            return
        points_dict = {}
        for _, row in part_data.iterrows():
            idx = row['index']
            x = row['x'] * w
            y = row['y'] * h
            x_scaled = cx + (x - cx) * scale_factor
            y_scaled = cy + (y - cy) * scale_factor
            points_dict[idx] = (int(x_scaled), int(y_scaled))

        for x, y in points_dict.values():
            cv2.circle(img, (x, y), 1, color, -1)

        for start_idx, end_idx in connections:
            if start_idx in points_dict and end_idx in points_dict:
                cv2.line(img, points_dict[start_idx], points_dict[end_idx], color, 1)

    # Face
    draw_part(frame_data[frame_data['part'] == 'face'], face_connections, (0, 255, 0))

    # Hands (both)
    for hand_idx in [0, 1]:
        hand_data = frame_data[(frame_data['part'] == 'hand') & (frame_data['hand_index'] == hand_idx)]
        draw_part(hand_data, hand_connections, (255, 0, 0))

    # Pose
    draw_part(frame_data[frame_data['part'] == 'pose'], pose_connections, (0, 0, 255))

    # Show playback
    cv2.imshow("Playback", img)
    if cv2.waitKey(30) & 0xFF == 27:
        break

cv2.destroyAllWindows()
