import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import *
import os, math, time
from src.slime import DesktopPet
from src.handpose import HandPose, Hand
from src.voicecontrol import voice_control_thread
import multiprocessing as mp

def get_screen_resolution():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    primary_screen = app.primaryScreen()
    screen_size = primary_screen.size()
    width = screen_size.width()
    height = screen_size.height()
    return width, height

class MyPet(QWidget):
    def __init__(self, scale_factor=1.0):
        super().__init__()
        width, height = get_screen_resolution()
        # 设置窗口分辨率
        self.width = width
        self.height = height
        self.scale_factor = scale_factor
        # 初始化UI
        self.initUI()
        # 初始化工具
        self.slime = DesktopPet(self.pet_image.width(), width, height)
        self.handpose = HandPose(width, height)
        # 初始化监听模块
        # 将语音控制与按键空格绑定
        self.tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
        self.prev_content = "" 
        # 语音识别模块进程
        self.voice_control_process = mp.Process(target=voice_control_thread)
        self.voice_control_process.start()

        self.run()

    def initUI(self):
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, self.width, self.height)

        # 加载图片
        self.pet_image = QLabel(self)
        pet_picture = QPixmap('asset/slime.png')
        scaled_pixmap = pet_picture.scaled(QSize(int(pet_picture.width()*self.scale_factor), 
                                                 int(pet_picture.height()*self.scale_factor)), Qt.KeepAspectRatio)
        self.pet_image.setPixmap(scaled_pixmap)
        self.pet_image.setGeometry(self.width//2, self.height//2, 110, 110)

        # 加载手的图片
        self.hand_grasp_image = QLabel(self)
        hand_grasp_picture = QPixmap('asset/hand_grasp.png')
        scaled_pixmap = hand_grasp_picture.scaled(QSize(int(hand_grasp_picture.width()*self.scale_factor),
                                                        int(hand_grasp_picture.height()*self.scale_factor)), Qt.KeepAspectRatio)
        self.hand_grasp_image.setPixmap(scaled_pixmap)
        self.hand_grasp_image.setGeometry(self.width//4, self.height//4, scaled_pixmap.width(), scaled_pixmap.height())
        self.hand_grasp_image.setAttribute(Qt.WA_TranslucentBackground)
        self.hand_grasp_image.setVisible(False)

        self.hand_loose_image = QLabel(self)
        hand_loose_picture = QPixmap('asset/hand_loose.png')
        scaled_pixmap = hand_loose_picture.scaled(QSize(int(hand_loose_picture.width()*self.scale_factor),
                                                        int(hand_loose_picture.height()*self.scale_factor)), Qt.KeepAspectRatio)
        self.hand_loose_image.setPixmap(scaled_pixmap)
        self.hand_loose_image.setGeometry(self.width//4, self.height//4, scaled_pixmap.width(), scaled_pixmap.height())
        self.hand_loose_image.setAttribute(Qt.WA_TranslucentBackground)
        self.hand_loose_image.setVisible(True)

        # 初始化鼠标位置
        self.oldPos = self.pos()

    def hand_update(self):
        # 通过中指计算当前收的角度
        def angle_calculate(point1, point2):
            x1, y1 = point1
            x2, y2 = point2
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            angle = math.asin((y2 - y1) / (x2 - x1)/ length)
            return angle
        # if self.hand is not None:
        #     print(angle_calculate(self.hand.finger_info['middle'][0][:2], self.hand.finger_info['middle'][-1][:2]), self.hand.finger_info['middle'][-1][:2])
        # 获取当前识别到的手
        hands = self.handpose.get_hand_landmarks()
        if len(hands) == 0:
            self.hand = None
            return
        hand = hands[0]
        self.hand = Hand(hand)

    def hand_grab_slime(self):
        dis = ((self.hand.x - self.slime.x) ** 2 + (self.hand.y - self.slime.y) ** 2) ** 0.5
        if dis < 300 and self.slime.is_grabbed:
            # 如果手部与slime的距离小于250，且slime已经被抓住，则更新slime的位置，此次距离判断较大是为了防止经常脱手
            self.slime.set_position(self.hand.x, self.hand.y)
        elif dis < 50 and not self.slime.is_grabbed:  # 如果手部与slime的距离小于100，且slime没有被抓住，避免出现像吸住了一样的情况
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
    
    def global_update(self):
        # 获取手部位置关键点
        self.hand_update()
        if self.hand is not None:
            if self.hand.is_grab():
                self.hand_grab_slime()
                self.hand_grasp_image.setVisible(True)
                self.hand_loose_image.setVisible(False)
            else:
                self.hand_grasp_image.setVisible(False)
                self.hand_loose_image.setVisible(True)
        self.slime.update()

    def run(self):
        # 设置动画效果
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(33)  # 每秒更新一次

    def animate(self):
        self.global_update()
        self.pet_image.setGeometry(int(self.slime.x), int(self.slime.y), self.pet_image.width(), self.pet_image.height())
        if self.hand is not None:
            self.hand_grasp_image.setGeometry(int(self.hand.x), int(self.hand.y), self.hand_grasp_image.width(), self.hand_grasp_image.height())
            self.hand_loose_image.setGeometry(int(self.hand.x), int(self.hand.y), self.hand_loose_image.width(), self.hand_loose_image.height())

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # 判断鼠标在不在pet的范围内
        if event.x() < self.pet_image.x() or event.x() > self.pet_image.x() + self.pet_image.width() or event.y() < self.pet_image.y() or event.y() > self.pet_image.y() + self.pet_image.height():
            return
        # 计算鼠标移动的偏移量
        delta = QPoint(event.globalPos() - self.oldPos)
        # 更新窗口位置
        self.pet_image.setGeometry(self.pet_image.x() + delta.x(), self.pet_image.y() + delta.y(), self.pet_image.width(), self.pet_image.height())
        self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        # 鼠标释放时的事件
        pass

    def keyPressEvent(self, event):
        # 检查是否按下了 ESC 键
        if event.key() == Qt.Key_Escape:
            self.close()  # 关闭窗口
            QApplication.quit()  # 退出整个应用程序
    
    def __del__(self):
        self.voice_control_process.terminate()
        self.voice_control_process.join()
        # 关闭语音识别进程
        self.voice_control_process.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = MyPet()
    pet.show()
    sys.exit(app.exec_())