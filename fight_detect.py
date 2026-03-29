import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
import warnings
import os

# 🔇 Suppress warnings (clean output)
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load models
print("Loading YOLO model...")
yolo_model = YOLO("yolov8n.pt")  # auto-downloads if not present

print("Loading MediaPipe pose...")
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Parameters
AGGRESSION_THRESHOLD = 6
FIGHT_CONFIRMATION_FRAMES = 5

def movement_intensity(landmarks):
    points = []
    for lm in landmarks.landmark:
        points.append([lm.x, lm.y])
    points = np.array(points)

    if len(points) < 2:
        return 0

    diff = np.linalg.norm(points[1:] - points[:-1], axis=1)
    return diff.mean() * 100


def detect_fight(video_path):
    
    print(f"\nStarting detection on: {video_path}")

    if not os.path.exists(video_path):
        print("ERROR: Video file not found")
        return "Error: File not found"

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("ERROR: Cannot open video")
        return "Error: Cannot open video"

    fight_frame_counter = 0
    fight_detected = False
    frame_count = 0

    MAX_FRAMES = 120     # limit processing
    FRAME_SKIP = 3       # skip frames for speed

    intensity_list = []
    max_intensity = 0
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("End of video or cannot read frame")
            break

        frame_count += 1

        if frame_count > MAX_FRAMES:
            print("Reached frame limit")
            break

        if frame_count % FRAME_SKIP != 0:
            continue

        # Resize (huge speed boost)
        frame = cv2.resize(frame, (480, 270))

        # YOLO person detection
        results = yolo_model(frame, classes=[0], verbose=False)
        person_count = sum(len(r.boxes) for r in results)

        print(f"Frame {frame_count}: Persons detected = {person_count}")

        if person_count < 2:
            continue

        # Pose detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(rgb)

        if pose_results.pose_landmarks:
            intensity = movement_intensity(pose_results.pose_landmarks)
            print(f"Movement intensity: {intensity:.2f}")

            if intensity > AGGRESSION_THRESHOLD:
                fight_frame_counter += 1
            else:
                fight_frame_counter = max(0, fight_frame_counter - 1)

            if fight_frame_counter >= FIGHT_CONFIRMATION_FRAMES:
                fight_detected = True
                print("Fight detected early, stopping...")
                break
            intensity_list.append(float(intensity))
            max_intensity = max(max_intensity, intensity)

    cap.release()

    return {
    "prediction": "Fight" if fight_detected else "No Fight",
    "confidence": round(0.7 + 0.2 * fight_detected, 2),
    "intensity_data": intensity_list[:30],
    "max_intensity": round(max_intensity, 2)
}


# 🔹 Run test
if __name__ == "__main__":
    result = detect_fight("fight.mp4")  # put your video here
    print("Final Output:", result)