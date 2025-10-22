import cv2
import pandas as pd
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

face_connections = mp_face_mesh.FACEMESH_TESSELATION
hand_connections = mp_hands.HAND_CONNECTIONS
pose_connections = mp_pose.POSE_CONNECTIONS

# Load CSV and skip bad lines
df = pd.read_csv("howareyou.csv", on_bad_lines='skip')

# Convert to numeric and drop bad rows
df['x'] = pd.to_numeric(df['x'], errors='coerce')
df['y'] = pd.to_numeric(df['y'], errors='coerce')
df['z'] = pd.to_numeric(df['z'], errors='coerce')
df = df.dropna()

# Set output size
w, h =  1200,700 

# Parts we expect
parts = ['face', 'hand', 'pose']

# Group by frames
min_points = df[df['part'] == 'face'].shape[0]
points_per_frame = 468  # landmarks per face
n_frames = min_points // points_per_frame

print(f"Total frames: {n_frames}")

scale_factor = 2
frame_len = len(df) // n_frames

for frame_idx in range(n_frames):
    img = np.zeros((h, w, 3), dtype=np.uint8)

    frame_data = df.iloc[frame_idx * frame_len: (frame_idx + 1) * frame_len]

    # ✅ compute global center for this frame
    all_xs = frame_data['x'] * w
    all_ys = frame_data['y'] * h
    cx, cy = np.mean(all_xs), np.mean(all_ys)

    for part in parts:
        part_data = frame_data[frame_data['part'] == part]

        if part_data.empty:
            continue

        # Build dict of scaled points: index -> (x, y)
        points_dict = {}
        for _, row in part_data.iterrows():
            idx = int(row['index'])
            x = row['x'] * w
            y = row['y'] * h
            x_scaled = cx + (x - cx) * scale_factor
            y_scaled = cy + (y - cy) * scale_factor
            points_dict[idx] = (int(x_scaled), int(y_scaled))

        # choose color and connections per part
        if part == 'face':
            color = (0, 255, 0)
            connections = face_connections
        elif part == 'hand':
            color = (255, 0, 0)
            connections = hand_connections
        elif part == 'pose':
            color = (0, 0, 255)
            connections = pose_connections
        else:
            continue

        # draw points
        for x, y in points_dict.values():
            cv2.circle(img, (x, y), 1, color, -1)

        # draw connections
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx in points_dict and end_idx in points_dict:
                cv2.line(
                    img,
                    points_dict[start_idx],
                    points_dict[end_idx],
                    color,
                    1
                )

    cv2.imshow("Face+Hands+Pose Animation (MediaPipe style)", img)
    if cv2.waitKey(30) & 0xFF == 27:
        break

cv2.destroyAllWindows()
