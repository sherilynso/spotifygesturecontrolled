import cv2
import mediapipe as mp
import pyautogui
import time
import math

# Setup
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)
draw = mp.solutions.drawing_utils

last_action_time = 0
cooldown = 1.5
pinch_cooldown = 0.3 # seconds
prev_pinch_dist = None  # For motion-based volume control

def distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def count_fingers(lm):
    count = 0
    if lm[8].y < lm[6].y: count += 1    # Index
    if lm[12].y < lm[10].y: count += 1  # Middle
    if lm[16].y < lm[14].y: count += 1  # Ring
    if lm[20].y < lm[18].y: count += 1  # Pinky
    if lm[4].x > lm[3].x: count += 1    # Thumb
    return count

def is_fist(lm):
    return all(lm[tip].y > lm[tip - 2].y for tip in [8, 12, 16, 20])

def trigger_action(name, key):
    global last_action_time
    if time.time() - last_action_time > cooldown:
        print(f"{name} detected → Sending: {key}")
        pyautogui.press(key)
        last_action_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark
            fingers = count_fingers(lm)

            # Gesture-based actions
            if is_fist(lm):
                trigger_action("Fist", "playpause")
            elif fingers == 3:
                trigger_action("3 fingers", "prevtrack")
            elif fingers == 4:
                trigger_action("4 fingers", "nexttrack")
            elif fingers == 5:
                trigger_action("Open palm", "playpause")

            # Pinch motion detection
            pinch_dist = distance(lm[4], lm[8])  # Thumb tip to index tip
            if prev_pinch_dist is not None:
                delta = pinch_dist - prev_pinch_dist
                steps = int(abs(delta) / 0.04)  # More steps = more volume change
                if delta > 0.05:
                    print("Pinch Wider → Volume Up x", steps)
                    for _ in range(steps):
                        pyautogui.press("volumeup")
                elif delta < -0.05:
                    print("Pinch Closer → Volume Down x", steps)
                    for _ in range(steps):
                        pyautogui.press("volumedown")
            prev_pinch_dist = pinch_dist

    cv2.imshow("Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



