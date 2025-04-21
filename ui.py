# ---------------- ui.py ----------------
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import pyautogui
import mediapipe as mp
from calibrator import calibrate
from gaze_tracker import get_eye_position, smooth_and_map
from gesture_handler import detect_gesture


class EyeTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eye Tracker Mouse")
        self.root.geometry("800x600")

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 16), fg="green")
        self.feedback_label.pack()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Start Calibration", command=self.start_calibration).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Exit", command=self.exit_app).pack(side=tk.RIGHT, padx=10)

        self.running = True
        self.calibrated = None
        self.calibrating = False

        self.cap = cv2.VideoCapture(0)
        self.screen_w, self.screen_h = pyautogui.size()
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)
        self.hands = mp.solutions.hands.Hands(max_num_hands=1)

        self.video_thread = threading.Thread(target=self.video_loop)
        self.video_thread.start()

    def start_calibration(self):
        self.feedback_label.config(text="Calibrating...")
        threading.Thread(target=self._run_calibration).start()

    def _run_calibration(self):
        self.calibrating = True
        self.calibrated = calibrate(self.cap, self.face_mesh, self.screen_w, self.screen_h)
        self.calibrating = False

    def exit_app(self):
        self.running = False
        self.cap.release()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def video_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            img_h, img_w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_results = self.face_mesh.process(rgb)
            hand_results = self.hands.process(rgb)

            if self.calibrated and not self.calibrating and face_results.multi_face_landmarks:
                landmarks = face_results.multi_face_landmarks[0].landmark
                eye_x, eye_y = get_eye_position(landmarks, img_w, img_h)
                screen_x, screen_y = smooth_and_map(eye_x, eye_y, self.calibrated, self.screen_w, self.screen_h)
                pyautogui.moveTo(screen_x, screen_y, duration=0.05)

            if not self.calibrating and hand_results.multi_hand_landmarks:
                hand_landmarks = hand_results.multi_hand_landmarks[0].landmark
                detect_gesture(hand_landmarks, img_h, self.feedback_label)

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
