import tkinter as tk
import cv2
from .slime import DesktopPet
from .handpose import HandPose, Hand

class GlobalSetting():
    def __init__(self, root: tk.Tk):
        self.slime = DesktopPet(root)
        self.handpose = HandPose(root)
        self.hand = None
        self.root = root
        self.run()
        

    def run(self):
        self.update()
        self.root.after(100, self.run)

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
        print(dis)
        if dis < 250:
            self.slime.x = self.hand.x
            self.slime.y = self.hand.y


    def update(self):
        # 获取手部位置关键点
        self.hand_update()
        if self.hand is not None:
            # print(self.hand.x, self.hand.y)
            print(self.slime.x, self.slime.y)
            print(self.hand.is_grab())
            if self.hand.is_grab():
                self.hand_grab_slime()
                self.slime.update()

if __name__ == "__main__":
    root = tk.Tk()
    global_setting = GlobalSetting(root)
    while True:
        global_setting.update()
    root.mainloop()