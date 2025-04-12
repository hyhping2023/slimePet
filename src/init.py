import tkinter as tk
import os, math
from .slime import DesktopPet
from .handpose import HandPose, Hand
from .voicecontrol import voice_control_thread
import multiprocessing as mp

class GlobalSetting():
    def __init__(self, root: tk.Tk):
        self.slime = DesktopPet(root)
        self.handpose = HandPose(root)
        self.hand = None
        self.root = root
        # 将语音控制与按键空格绑定
        self.tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
        self.prev_content = "" 
        # 语音交互模块进程
        # mp.Process(target=voice_control_thread).start()
        self.run()
        

    def run(self):
        self.update()
        # self.load_voice_record()
        self.root.after(16, self.run)

    def hand_update(self):
        # 通过中指计算当前收的角度
        def angle_calculate(point1, point2):
            x1, y1 = point1
            x2, y2 = point2
            print(x1, y1, x2, y2)
            angle = math.asin((y2 - y1) / (x2 - x1))
            return angle
        if self.hand is not None:
            print(angle_calculate(self.hand.finger_info['middle'][0][:2], self.hand.finger_info['middle'][-1][:2]), self.hand.finger_info['middle'][-1][:2])
        # 获取当前识别到的手
        hands = self.handpose.get_hand_landmarks()
        if len(hands) == 0:
            self.hand = None
            return
        hand = hands[0]
        self.hand = Hand(hand)

    def hand_grab_slime(self):
        dis = ((self.hand.x - self.slime.x) ** 2 + (self.hand.y - self.slime.y) ** 2) ** 0.5
        print(dis)
        if dis < 250:
            self.slime.x = self.hand.x
            self.slime.y = self.hand.y

    def load_voice_record(self,):
        if not os.path.exists(self.tmp_dir):
            return None
        with open(self.tmp_dir, "r") as f:
            # 读取文件内容
            content = f.read()
        if content != self.prev_content:
            self.prev_content = content
            print("读取到新内容：", content)
            return content
        return None
        

    def update(self):
        # 获取手部位置关键点
        self.hand_update()
        self.slime.update()
        if self.hand is not None:
            # print(self.hand.x, self.hand.y)
            print(self.slime.x, self.slime.y)
            print(self.hand.is_grab())
            if self.hand.is_grab():
                self.hand_grab_slime()
                self.slime.update()
        # with AudioToTextRecorder() as recorder:
        #     print("Transcription: ", recorder.text())

if __name__ == "__main__":
    root = tk.Tk()
    global_setting = GlobalSetting(root)
    while True:
        global_setting.update()
    root.mainloop()