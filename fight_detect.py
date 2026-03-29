import cv2
import numpy as np
import warnings
import os

warnings.filterwarnings("ignore")

# Lightweight HOG detector — no PyTorch needed
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

AGGRESSION_THRESHOLD = 7
FIGHT_CONFIRMATION_FRAMES = 5

def movement_intensity(prev_frame, curr_frame):
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

        # HOG person detection instead of YOLO
        boxes, _ = hog.detectMultiScale(frame, winStride=(8, 8), padding=(4, 4), scale=1.05)
        if len(boxes) < 2:
            prev_frame = frame
            continue

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
