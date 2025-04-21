import time
import pyautogui

prev_index_y = None
prev_middle_y = None
last_left_click = 0
last_right_click = 0
click_cooldown = 0.5


def detect_gesture(hand_landmarks, img_h, feedback_label):
    global prev_index_y, prev_middle_y, last_left_click, last_right_click
    index_y = hand_landmarks[8].y * img_h
    middle_y = hand_landmarks[12].y * img_h
    current_time = time.time()

    if prev_index_y and (prev_index_y - index_y > 25):
        if current_time - last_left_click > click_cooldown:
            pyautogui.click()
            feedback_label.config(text="Left Click")
            last_left_click = current_time

    if prev_middle_y and (prev_middle_y - middle_y > 25):
        if current_time - last_right_click > click_cooldown:
            pyautogui.rightClick()
            feedback_label.config(text="Right Click")
            last_right_click = current_time

    prev_index_y = index_y
    prev_middle_y = middle_y