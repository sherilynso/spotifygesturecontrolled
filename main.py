import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time
import math

# Webcam setup
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1, detectionCon=0.7)

# Cooldowns
last_action_time = 0
cooldown = 1.5
prev_pinch_dist = None

def trigger_action(name, key):
    global last_action_time
    if time.time() - last_action_time > cooldown:
        print(f"{name} detected → Sending: {key}")
        pyautogui.press(key)
        last_action_time = time.time()

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hands, img = detector.findHands(frame)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        totalFingers = sum(fingers)
        lmList = hand["lmList"]

        if totalFingers == 0:
            trigger_action("Fist", "playpause")
        elif totalFingers == 3:
            trigger_action("3 fingers", "prevtrack")
        elif totalFingers == 4:
            trigger_action("4 fingers", "nexttrack")
        elif totalFingers == 5:
            trigger_action("Open Palm", "playpause")

        if lmList:
            thumb_tip = lmList[4]
            index_tip = lmList[8]
            pinch_dist = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])

            if prev_pinch_dist is not None:
                delta = pinch_dist - prev_pinch_dist
                steps = int(abs(delta) / 5)
                if delta > 10:
                    print("Pinch opened → Volume UP ×", steps)
                    for _ in range(steps):
                        pyautogui.press("volumeup")
                elif delta < -10:
                    print("Pinch closed → Volume DOWN ×", steps)
                    for _ in range(steps):
                        pyautogui.press("volumedown")
            prev_pinch_dist = pinch_dist

    cv2.imshow("Gesture Controller (cvzone)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
