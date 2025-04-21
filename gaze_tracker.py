# ---------------- gaze_tracker.py ----------------
import numpy as np
from collections import deque

x_buffer = deque(maxlen=5)
y_buffer = deque(maxlen=5)


def get_eye_position(landmarks, img_w, img_h):
    eye_idx = [33, 133, 159]
    x = int(np.mean([landmarks[i].x for i in eye_idx]) * img_w)
    y = int(np.mean([landmarks[i].y for i in eye_idx]) * img_h)
    return x, y


def smooth_and_map(eye_x, eye_y, calibrated, screen_w, screen_h):
    x_buffer.append(eye_x)
    y_buffer.append(eye_y)
    smooth_x = int(np.mean(x_buffer))
    smooth_y = int(np.mean(y_buffer))
    (gx_min, gy_min), (gx_max, gy_max) = calibrated
    x = np.interp(smooth_x, [gx_min[0], gx_max[0]], [0, screen_w])
    y = np.interp(smooth_y, [gy_min[1], gy_max[1]], [0, screen_h])
    return x, y