import csv
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture("MVI_9921.MOV")

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh, \
mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands, \
mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    with open("howareyou.csv", mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["frame", "part", "index", "hand_index", "x", "y", "z"])
        writer.writeheader()

        frame_count = 0

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            frame_count += 1
            image_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False

            face_results = face_mesh.process(image_rgb)
            hand_results = hands.process(image_rgb)
            pose_results = pose.process(image_rgb)

            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            # Face
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
                    for landmark_idx, landmark in enumerate(face_landmarks.landmark):
                        writer.writerow({
                            "frame": frame_count,
                            "part": "face",
                            "index": landmark_idx,
                            "hand_index": -1,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })

            # Hands
            if hand_results.multi_hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=hand_landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style()
                    )
                    for landmark_idx, landmark in enumerate(hand_landmarks.landmark):
                        writer.writerow({
                            "frame": frame_count,
                            "part": "hand",
                            "index": landmark_idx,
                            "hand_index": hand_idx,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })

            # Pose
            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=pose_results.pose_landmarks,
                    connections=mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=2)
                )
                for landmark_idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
                    writer.writerow({
                        "frame": frame_count,
                        "part": "pose",
                        "index": landmark_idx,
                        "hand_index": -1,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })

            # Show live preview
            cv2.imshow("Recording", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()
