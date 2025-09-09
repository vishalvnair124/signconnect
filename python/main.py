import csv
import cv2
import mediapipe as mp

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

# Open CSV file once and write header
with open("landmarks.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["part", "index", "x", "y", "z"])
    writer.writeheader()

    # Initialize all three models
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

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip and convert to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process each solution
            result_face = face_mesh.process(image)
            result_hands = hands.process(image)
            result_pose = pose.process(image)

            # Draw and save landmarks
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Face
            if result_face.multi_face_landmarks:
                for face_landmarks in result_face.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
                    for i, landmark in enumerate(face_landmarks.landmark):
                        writer.writerow({
                            "part": "face",
                            "index": i,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })

            # Hands
            if result_hands.multi_hand_landmarks:
                for hand_landmarks in result_hands.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=hand_landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style()
                    )
                    for i, landmark in enumerate(hand_landmarks.landmark):
                        writer.writerow({
                            "part": "hand",
                            "index": i,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })

            # Pose
            if result_pose.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=result_pose.pose_landmarks,
                    connections=mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
                for i, landmark in enumerate(result_pose.pose_landmarks.landmark):
                    writer.writerow({
                        "part": "pose",
                        "index": i,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })

            # Show the frame
            cv2.imshow('MediaPipe Face+Hands+Pose', image)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()
