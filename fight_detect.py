import cv2
import numpy as np
from ultralytics import YOLO
import warnings
import os

# 🔇 Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load YOLO model
print("Loading YOLO model...")
yolo_model = YOLO("yolov8n.pt")  # auto-downloads if not present

# Parameters
AGGRESSION_THRESHOLD = 7  # tweak based on motion intensity
FIGHT_CONFIRMATION_FRAMES = 5

def movement_intensity(prev_frame, curr_frame):
    """Calculate simple motion intensity using frame difference."""
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_prev, gray_curr)
    return np.mean(diff)

def detect_fight(video_path):
    if not os.path.exists(video_path):
        return {"error": "File not found"}

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video"}

    fight_frame_counter = 0
    fight_detected = False
    frame_count = 0
    MAX_FRAMES = 120
    FRAME_SKIP = 2
    intensity_list = []
    max_intensity = 0
    prev_frame = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count > MAX_FRAMES:
            break
        if frame_count % FRAME_SKIP != 0:
            continue

        frame = cv2.resize(frame, (480, 270))

        # YOLO person detection
        results = yolo_model(frame, classes=[0], verbose=False)
        person_count = sum(len(r.boxes) for r in results)
        if person_count < 2:
            prev_frame = frame
            continue

        # Motion intensity
        if prev_frame is not None:
            intensity = movement_intensity(prev_frame, frame)
            intensity_list.append(float(intensity))
            max_intensity = max(max_intensity, intensity)

            if intensity > AGGRESSION_THRESHOLD:
                fight_frame_counter += 1
            else:
                fight_frame_counter = max(0, fight_frame_counter - 1)

            if fight_frame_counter >= FIGHT_CONFIRMATION_FRAMES:
                fight_detected = True
                break

        prev_frame = frame

    cap.release()
    return {
        "prediction": "Fight" if fight_detected else "No Fight",
        "confidence": round(0.7 + 0.2 * fight_detected, 2),
        "intensity_data": intensity_list[:30],
        "max_intensity": round(max_intensity, 2)
    }

# 🔹 Run test
if __name__ == "__main__":
    result = detect_fight("fight.mp4")
    print(result)