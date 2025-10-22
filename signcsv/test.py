import cv2
import pandas as pd
import numpy as np
import mediapipe as mp
import glob
import os

# === MediaPipe landmark connections ===
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

FACE_CONNECTIONS = mp_face_mesh.FACEMESH_TESSELATION
HAND_CONNECTIONS = mp_hands.HAND_CONNECTIONS
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# === Display parameters ===
FRAME_W, FRAME_H = 1200, 700
SCALE_FACTOR = 1  # zoom in a bit
FPS = 30 # Frames per second for the output video


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


def create_video_from_csv(csv_filepath):
    """
    Reads a landmark CSV file, processes it, and saves it as an MP4 video.
    The output video will have the same name as the CSV file.
    """
    output_filename = os.path.splitext(csv_filepath)[0] + '.mp4'
    print(f"\n--- Processing '{csv_filepath}' -> '{output_filename}' ---")

    # === Load CSV landmarks ===
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_filepath}. Skipping.")
        return

    # Clean & convert columns
    for col in ['frame', 'index', 'hand_index', 'x', 'y', 'z']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)
    df = df.sort_values(by='frame')
    df['frame'] = df['frame'].astype(int)
    df['index'] = df['index'].astype(int)
    df['hand_index'] = df['hand_index'].astype(int)

    if df.empty:
        print(f"Warning: CSV file '{csv_filepath}' is empty or has no valid data. Skipping.")
        return

    n_frames = df['frame'].max()
    print(f"🎞️ Total frames to process: {n_frames}")

    # === Video Writer Setup ===
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Use 'mp4v' for .mp4 files
    video_writer = cv2.VideoWriter(output_filename, fourcc, FPS, (FRAME_W, FRAME_H))

    if not video_writer.isOpened():
        print("Error: Could not open video writer. Check OpenCV installation.")
        return

    # === Processing and Video Saving loop ===
    for frame_idx in range(1, n_frames + 1):
        canvas = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
        frame_data = df[df['frame'] == frame_idx]

        if not frame_data.empty:
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

        video_writer.write(canvas)
        
        if frame_idx % 100 == 0 or frame_idx == n_frames:
            print(f"   Processed frame {frame_idx}/{n_frames}")

    # === Finalize ===
    video_writer.release()
    print(f"✅ Video saved successfully as '{output_filename}'")


# === Main Execution ===
if __name__ == "__main__":
    # Find all csv files in the current directory
    csv_files = glob.glob('*.csv')
    
    if not csv_files:
        print("No CSV files found in the current directory. Please place CSV files here.")
    else:
        print(f"Found {len(csv_files)} CSV files to process: {', '.join(csv_files)}")
        for csv_file in csv_files:
            create_video_from_csv(csv_file)
    
    print("\n--- All tasks complete. ---")

