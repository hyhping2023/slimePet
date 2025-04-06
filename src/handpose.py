import cv2
import mediapipe as mp
import warnings
import tkinter as tk

class HandPose:
    def __init__(self, root: tk.Tk):
        # 初始化MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        # 获取屏幕分辨率
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        

    # 得到手部位置关键点
    def get_hand_landmarks(self, ):
        ret, frame = self.cap.read()
        if not ret:
            warnings.warn("Failed to capture image from camera.")
            return []
        # 转换为RGB格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 检测手部
        results = self.hands.process(rgb_frame)
        hand_landmarks = []
        hands = []
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 按照手掌分布规律使用字典进行储存
                hand_landmarks_dict = {"wrist": [], "thumb": [], "index": [], "middle": [], "ring": [], "pinky": []}
                # 画出手部关键点
                for id, landmark in enumerate(hand_landmarks.landmark):
                    if id == 0:
                        hand_landmarks_dict["wrist"] = [(landmark.x*self.screen_width, landmark.y*self.screen_height)]
                    elif id <= 4:
                        hand_landmarks_dict["thumb"].append((landmark.x*self.screen_width, landmark.y*self.screen_height))
                    elif id <= 8:
                        hand_landmarks_dict["index"].append((landmark.x*self.screen_width, landmark.y*self.screen_height))
                    elif id <= 12:
                        hand_landmarks_dict["middle"].append((landmark.x*self.screen_width, landmark.y*self.screen_height))
                    elif id <= 16:
                        hand_landmarks_dict["ring"].append((landmark.x*self.screen_width, landmark.y*self.screen_height))
                    elif id <= 20:
                        hand_landmarks_dict["pinky"].append((landmark.x*self.screen_width, landmark.y*self.screen_height))
                hands.append(hand_landmarks_dict)
        return hands
    
if __name__ == "__main__":
    root = tk.Tk()
    handpose = HandPose(root)
    while True:
        hands = handpose.get_hand_landmarks()
        print(hands)
        print(handpose.screen_width, handpose.screen_height)

        import time
        time.sleep(1)
