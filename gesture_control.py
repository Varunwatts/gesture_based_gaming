import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.7):
        self.hands_module = mp.solutions.hands
        self.hands = self.hands_module.Hands(max_num_hands=maxHands, min_detection_confidence=detectionCon)
        self.drawing = mp.solutions.drawing_utils
        self.hand_position = "center"

    def detect_hand(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                cx = int(hand_landmarks.landmark[9].x * w)  # Landmark 9: base of index finger
                if cx < w / 3:
                    self.hand_position = "left"
                elif cx > 2 * w / 3:
                    self.hand_position = "right"
                else:
                    self.hand_position = "center"
                self.drawing.draw_landmarks(frame, hand_landmarks, self.hands_module.HAND_CONNECTIONS)
        return frame, self.hand_position
