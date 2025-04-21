# ---------------- calibrator.py ----------------
import time
import cv2
import numpy as np
from gaze_tracker import get_eye_position

calibration_points = [(0.1, 0.1), (0.9, 0.1), (0.1, 0.9), (0.9, 0.9)]


def calibrate(cap, face_mesh, screen_w, screen_h):
    calibration_data = []
    for norm_x, norm_y in calibration_points:
        abs_x = int(screen_w * norm_x)
        abs_y = int(screen_h * norm_y)
        import pyautogui
        pyautogui.moveTo(abs_x, abs_y, duration=0.5)
        time.sleep(1)

        samples = []
        for _ in range(15):
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            img_h, img_w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                eye_x, eye_y = get_eye_position(landmarks, img_w, img_h)
                samples.append((eye_x, eye_y))
        avg_eye = np.mean(samples, axis=0)
        calibration_data.append(avg_eye)

    gx_min, gx_max = calibration_data[0], calibration_data[1]
    gy_min, gy_max = calibration_data[0], calibration_data[2]
    return (gx_min, gy_min), (gx_max, gy_max)
