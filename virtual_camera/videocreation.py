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
# Make sure the CSV file "howareyou.csv" is in the same directory
try:
    df = pd.read_csv("default.csv")
except FileNotFoundError:
    print("Error: 'howareyou.csv' not found. Please ensure the CSV file is in the same directory as the script.")
    exit()


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
FPS = 30 # Frames per second for the output video
OUTPUT_FILENAME = "landmark_video.mp4"

n_frames = df['frame'].max()
print(f"🎞️ Total frames to process: {n_frames}")

# === Video Writer Setup ===
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Use 'mp4v' for .mp4 files
video_writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, FPS, (FRAME_W, FRAME_H))

if not video_writer.isOpened():
    print("Error: Could not open video writer. Check OpenCV installation.")
    exit()

# === Utility: Draw landmarks & connections ===
def draw_landmarks(image, part_data, connections, color, center_x, center_y):
    if part_data.empty:
        return

    points = {}
    for _, row in part_data.iterrows():
        # Scale landmark coordinates to frame dimensions
        x = row['x'] * FRAME_W
        y = row['y'] * FRAME_H
        
        # Apply scaling factor around the center point
        x = center_x + (x - center_x) * SCALE_FACTOR
        y = center_y + (y - center_y) * SCALE_FACTOR
        points[row['index']] = (int(x), int(y))

    # Draw landmark dots
    for pt in points.values():
        cv2.circle(image, pt, 2, color, -1)

    # Draw connections between landmarks
    if connections:
        for start_idx, end_idx in connections:
            if start_idx in points and end_idx in points:
                cv2.line(image, points[start_idx], points[end_idx], color, 1)

# === Processing and Video Saving loop ===
print(f"📹 Creating video '{OUTPUT_FILENAME}'...")

for frame_idx in range(1, n_frames + 1):
    # Create a blank black canvas for each frame
    canvas = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)

    # Get all data for the current frame
    frame_data = df[df['frame'] == frame_idx]

    if not frame_data.empty:
        # Compute center of all landmarks for this frame (for scaling around the center)
        cx = (frame_data['x'] * FRAME_W).mean()
        cy = (frame_data['y'] * FRAME_H).mean()

        # Draw face landmarks
        face_data = frame_data[frame_data['part'] == 'face']
        draw_landmarks(canvas, face_data, FACE_CONNECTIONS, (0, 255, 0), cx, cy) # Green

        # Draw both hands
        hand_colors = {0: (255, 0, 0), 1: (0, 165, 255)} # Blue and Orange
        for hand_idx, color in hand_colors.items():
            hand_data = frame_data[(frame_data['part'] == 'hand') & (frame_data['hand_index'] == hand_idx)]
            draw_landmarks(canvas, hand_data, HAND_CONNECTIONS, color, cx, cy)

        # Draw pose landmarks
        pose_data = frame_data[frame_data['part'] == 'pose']
        draw_landmarks(canvas, pose_data, POSE_CONNECTIONS, (128, 0, 128), cx, cy) # Purple

    # Write the completed frame to the video file
    video_writer.write(canvas)
    
    # Optional: Print progress
    if frame_idx % 100 == 0 or frame_idx == n_frames:
        print(f"   Processed frame {frame_idx}/{n_frames}")


# === Finalize ===
# Release the video writer object
video_writer.release()
print(f"✅ Video saved successfully as '{OUTPUT_FILENAME}'")

# The original display code is removed as we are saving to a file.
# If you want to display the video as well, you can add this back in.
# cv2.destroyAllWindows()
