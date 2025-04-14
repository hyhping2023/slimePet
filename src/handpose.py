import cv2
import mediapipe as mp
import warnings

class Hand:
    def __init__(self, hand_landmarks:dict):
        self.finger_info = {
            "thumb": hand_landmarks["thumb"],
            "index": hand_landmarks["index"],
            "middle": hand_landmarks["middle"],
            "ring": hand_landmarks["ring"],
            "pinky": hand_landmarks["pinky"]
        }
        self.wrist = hand_landmarks["wrist"]

        # physics properties
        self.x, self.y = self.finger_info["middle"][0][:2]


    def is_grab(self):
        grab_threshold = 0
        def is_in_hand(point:list, reference:list, ):
            vertical, horizontal = False, False
            # 水平方向考虑
            reference.sort(key=lambda x: x[0])
            if reference[0][0] <= point[0] <= reference[1][0]:
                horizontal = True
            # 垂直方向考虑
            reference.sort(key=lambda x: x[1])
            if reference[0][1] <= point[1] <= reference[1][1]:
                vertical = True
            # 一个方向为真即可判断为抓住
            return vertical or horizontal
        for finger in self.finger_info.values():
            if is_in_hand(finger[-1], [finger[0], self.wrist[0]]):
                grab_threshold += 1
        if grab_threshold >= 3:
            return True
        return False
    
    def judge_the_same_hand(self, other_hand: list[float, float]):
        def distance(point1, point2):
            return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
        # 计算手腕之间的距离
        dis = distance((self.x, self.y), other_hand)
        if dis < 200:
            return True
        return False

class HandPose:
    '''
    自己面朝的左上角为(0, 0)点，x轴向右，y轴向下
    '''
    def __init__(self, screen_width:int, screen_height:int):
        # 初始化MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        # 获取屏幕分辨率
        self.screen_width = screen_width
        self.screen_height = screen_height
        # 设置摄像头分辨率
        

    # 得到手部位置关键点
    def get_hand_landmarks(self, ):
        ret, frame = self.cap.read()
        # 将帧进行翻转
        frame = cv2.flip(frame, 1)
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
                    # 将返回值限制在屏幕范围内
                    if landmark.x > 1:
                        landmark.x = 1
                    if landmark.y > 1:
                        landmark.y = 1
                    if landmark.x < 0:
                        landmark.x = 0
                    if landmark.y < 0:
                        landmark.y = 0
                    # 将坐标转换为屏幕坐标 
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
        # return hands, frame, hand_landmarks
            return [hands[0]]
        return []
    
if __name__ == "__main__":
    handpose = HandPose(1920, 1080)
        
