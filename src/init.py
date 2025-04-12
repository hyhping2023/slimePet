import tkinter as tk
import os
from .slime import DesktopPet
from .handpose import HandPose, Hand
from .voicecontrol import voice_control_thread
import multiprocessing as mp
import time

class GlobalSetting():
    def __init__(self, root: tk.Tk):
        self.slime = DesktopPet(root)
        self.handpose = HandPose(root)
        self.hand = None
        self.root = root
        # 将语音控制与按键空格绑定
        # self.voice_recognize()
        self.tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
        self.prev_content = "" 
        mp.Process(target=voice_control_thread).start()
        self.run()
        

    def run(self):
        self.update()
        self.load_voice_record()
        self.root.after(16, self.run)

    def hand_update(self):
        # 获取当前识别到的手
        hands = self.handpose.get_hand_landmarks()
        if len(hands) == 0:
            self.hand = None
            return
        hand = hands[0]
        self.hand = Hand(hand)

    def hand_grab_slime(self):
        dis = ((self.hand.x - self.slime.x) ** 2 + (self.hand.y - self.slime.y) ** 2) ** 0.5
        if dis < 250:
            if not self.slime.is_grabbed:  # 如果之前没有被抓住
                self.slime.set_grabbed(True)
            self.slime.set_position(self.hand.x, self.hand.y)
        else:
            if self.slime.is_grabbed:  # 如果之前被抓住
                self.slime.set_grabbed(False)
                # 计算释放时的速度
                current_time = time.time()
                delta_time = current_time - self.slime.last_time
                if delta_time > 0.001:
                    # 增加速度计算的灵敏度
                    speed_multiplier = 1.5
                    self.slime.velocity_x = (self.hand.x - self.slime.last_x) / delta_time * speed_multiplier
                    self.slime.velocity_y = (self.hand.y - self.slime.last_y) / delta_time * speed_multiplier
                    # 限制最大速度
                    max_speed = 1500  # 增加最大速度限制
                    self.slime.velocity_x = max(min(self.slime.velocity_x, max_speed), -max_speed)
                    self.slime.velocity_y = max(min(self.slime.velocity_y, max_speed), -max_speed)

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
        if self.hand is not None:
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