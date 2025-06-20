import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os, math, time
from src.slime import DesktopPet
from src.handpose import HandPose, Hand
from src.voicecontrol import voice_control_thread
from src.language_server import generate, EMOTION_PROMPT, CHAT_HISTORY, scene_analyze, llm_emotion_query
from src.voicespeak import gpt_speak, change_voice
from src.face import facialExpression
from src.game import guess_game
from src.setting import SkinSelectionWindow
from src.utils import empty_remove
from src.config import AVAIABLE_VOICES, NAME2REALNAME
import multiprocessing as mp
import threading
import json
import logging
from src.voicespeak import initialize_voice

def get_screen_resolution():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    primary_screen = app.primaryScreen()
    screen_size = primary_screen.size()
    width = screen_size.width()
    height = screen_size.height()
    return width, height

def emotion_assist(user_emotion, people):
    result = scene_analyze(user_emotion, people=people)

def talk(prev_content, people="rencai", new_chat=False):
    response = generate(prev_content, people=people, new_chat=new_chat)

class QPicture(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        self.angle = 0

    def paintEvent(self, event):
        # 绘制旋转后的图片
        painter = QPainter(self)
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        painter.translate(-self.width() / 2, -self.height() / 2)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.restore()

class MyPet(QWidget):
    def __init__(self, scale_factor=1.0, fps:int = 120):
        super().__init__()
        initialize_voice()  # 主进程显式初始化
        width, height = get_screen_resolution()
        # 设置窗口分辨率
        self.width = width
        self.height = height
        self.scale_factor = scale_factor
        # 初始化UI
        self.reload_emotion()
        self.initUI()
        # 初始化工具
        self.slime = DesktopPet(self.pet_image.width(), width, height)
        self.handpose = HandPose(width, height)
        self.hand = None
        self.running = True  # 新增运行状态标志

        # 初始化监听模块
        # 将语音控制与按键空格绑定
        self.tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
        if os.path.exists(self.tmp_dir):
            # 删除临时文件
            with open(self.tmp_dir, "w") as f:
                f.write("")
        self.prev_content = "" 
        # 清除聊天历史
        with open(CHAT_HISTORY, "w", encoding="utf-8") as f:
            f.write("")

        # 语音识别模块进程
        self.voice_control_process = mp.Process(target=voice_control_thread)
        self.voice_control_process.start()
        # 表情识别模块
        self.facial_expression = facialExpression()
        # 记录slime0.2s前的速度，便于丢出
        self.prev_velocity = (time.time(), (0, 0))
        # 记录当前时间
        self.prev_time = time.time()
        self.no_hand_time = time.time()
        # 史莱姆状态
        self.free_times = 0
        self.user_emotion = 'neutral'
        # 线程和进程
        self.threads = []
        self.talk_process = None
        self.scene_process = None
        self.game_process = None
        # 当前状态
        self.status = "init"
        # 说话人
        self.speaker = "刻晴"
        try:
            change_voice(self.speaker)
        except Exception as e:
            logging.warning(f"语音设置失败: {e}")
            # 继续执行其他功能

    def closeEvent(self, event):
        # 终止所有子进程
        self.running = False
        self.voice_control_process.terminate()
        if self.talk_process and self.talk_process.is_alive():
            self.talk_process.terminate()
        if self.scene_process and self.scene_process.is_alive():
            self.scene_process.terminate()
        event.accept()
        if os.path.exists(self.tmp_dir):
            os.remove(self.tmp_dir)

    def reload_emotion(self):
        self.emotion = {
            "surprise": QMovie(setting_window.img[2]),
            "angry": QMovie(setting_window.img[5]),
            "happy": QMovie(setting_window.img[3]),
            "sad": QMovie(setting_window.img[5]),
            "neutral": QMovie(setting_window.img[0]),
            "nauseated": QMovie(setting_window.img[4]),
            "high_speed": QMovie(setting_window.img[1]),
        }


    def closeEvent(self, event):
        # 终止所有子进程
        self.running = False
        self.voice_control_process.terminate()
        if self.talk_process and self.talk_process.is_alive():
            self.talk_process.terminate()
        if self.scene_process and self.scene_process.is_alive():
            self.scene_process.terminate()
        event.accept()
        if os.path.exists(self.tmp_dir):
            os.remove(self.tmp_dir)

    def initUI(self):
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, self.width, self.height)

        # 加载图片
        self.pet_image = QLabel(self)
        self.movie = QMovie(self.emotion["neutral"])
        # 缩放GIF
        self.movie.setScaledSize(QSize(
            int(self.movie.scaledSize().width() * self.scale_factor),
            int(self.movie.scaledSize().height() * self.scale_factor)
        ))
        self.pet_image.setMovie(self.movie)
        self.movie.start()  # 开始播放动画
        self.pet_image.setGeometry(self.width//2, self.height//2, 110, 110)

        # 加载手的图片
        self.hand_grasp_image = QPicture(self)
        hand_grasp_picture = QPixmap('asset/hand_grasp.png')
        scaled_pixmap = hand_grasp_picture.scaled(QSize(int(hand_grasp_picture.width()*self.scale_factor),
                                                        int(hand_grasp_picture.height()*self.scale_factor)), Qt.KeepAspectRatio)
        # self.hand_grasp_image.setPixmap(scaled_pixmap)
        self.hand_grasp_image.pixmap = scaled_pixmap
        max_size = max(scaled_pixmap.width(), scaled_pixmap.height())
        self.hand_grasp_image.setGeometry(self.width//4, self.height//4, max_size, max_size)
        self.hand_grasp_image.setAttribute(Qt.WA_TranslucentBackground)
        self.hand_grasp_image.setVisible(False)

        self.hand_loose_image = QPicture(self)
        hand_loose_picture = QPixmap('asset/hand_loose.png')
        scaled_pixmap = hand_loose_picture.scaled(QSize(int(hand_loose_picture.width()*self.scale_factor),
                                                        int(hand_loose_picture.height()*self.scale_factor)), Qt.KeepAspectRatio)
        # self.hand_loose_image.setPixmap(scaled_pixmap)
        self.hand_loose_image.pixmap = scaled_pixmap
        self.hand_loose_image.setGeometry(self.width//4, self.height//4, max_size, max_size)
        self.hand_loose_image.setAttribute(Qt.WA_TranslucentBackground)
        self.hand_loose_image.setVisible(True)

        # 初始化鼠标位置
        self.oldPos = self.pos()

    def hand_update(self):
        # 通过中指计算当前收的角度
        def angle_calculate(point1, point2):
            """
            Calculate the angle between two points in 2D space.
            The angle is measured relative to the horizontal direction to the left.
            角度是顺时针的
            """
            x1, y1 = point1
            x2, y2 = point2
            angle = math.atan((y2 - y1) / (x2 - x1 + 1e-8)) * 180 / math.pi
            # 接下来计算手相对于水平向左的角度
            if x1 < x2:
                angle += 180
            while angle < 0:
                angle += 360
            while angle > 360:
                angle -= 360
            return angle
        if self.hand is not None:
            hand_angle = angle_calculate(self.hand.finger_info['middle'][0][:2], self.hand.finger_info['middle'][-1][:2])
            self.hand_grasp_image.angle = hand_angle
            self.hand_loose_image.angle = hand_angle
            self.hand_angle = hand_angle
        # 获取当前识别到的手
        hands = self.handpose.get_hand_landmarks()
        if len(hands) == 0:
            self.hand = None
            if time.time() - self.no_hand_time > 2:
                self.hand_grasp_image.setVisible(False)
                self.hand_loose_image.setVisible(False)
            return
        hand = hands[0]
        self.no_hand_time = time.time()
        self.hand = Hand(hand)
        self.hand_grasp_image.setVisible(True)
        self.hand_loose_image.setVisible(True)

    def hand_grab_slime(self):
        """
        Determine whether the hand should grab the slime or not based on the distance between them.

        If the hand and slime are closer than 300 pixels and the slime is already grabbed, the position of the slime is updated to the position of the hand.
        If the hand and slime are closer than 50 pixels and the slime is not grabbed, the slime is set to grabbed and its position is updated to the position of the hand.
        If the slime is grabbed and the hand and slime are more than 300 pixels apart, the slime is set to not grabbed.
        """
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

    def load_voice_record(self,):
        if not os.path.exists(self.tmp_dir):
            return None
        with open(self.tmp_dir, "r") as f:
            # 读取文件内容
            content = f.read()
        if content != self.prev_content and self.status == "free":
            self.prev_content = content
            if len(empty_remove(content)) == 0:
                return None
            print("读取到新内容：", content)
            if "猜" in content:
                self.start_game()
                return None
            self.status = 'busy_1'
            self.talk_process = mp.Process(target=talk, args=(content, self.speaker, ), daemon=True)
            self.talk_process.start()
            return content
        return None
    
    def start_game(self):
        self.status = "busy_3"
        self.game_process = mp.Process(target=guess_game, args=(self.speaker, ), daemon=True)
        self.game_process.start()
    
    def global_update(self):
        # 获取手部位置关键点
        if self.hand is not None:
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
        self.load_voice_record()
        self.pet_image.setGeometry(int(self.slime.x), int(self.slime.y), self.pet_image.width(), self.pet_image.height())
        if self.hand is not None:
            self.hand_grasp_image.setGeometry(int(self.hand.x), int(self.hand.y), self.hand_grasp_image.width(), self.hand_grasp_image.height())
            self.hand_loose_image.setGeometry(int(self.hand.x), int(self.hand.y), self.hand_loose_image.width(), self.hand_loose_image.height())
        if time.time() - self.prev_time > 1:
            if self.hand is None:
                self.hand_update()
            print(self.status)
            thread = threading.Thread(target=self.emotion_query, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.prev_time = time.time()

            # 更新表情显示
            if self.slime.is_nauseated:
                target_gif = self.emotion["nauseated"]
            elif self.slime.is_high_speed:
                target_gif = self.emotion["high_speed"]
            else:
                target_gif = self.emotion[self.slime.emotion]
                # print('3')
                if self.slime.change_emotion(self.user_emotion):
                    # print('4')
                    self.movie.stop()
                    self.movie = self.emotion[self.slime.emotion]
                    self.movie.setScaledSize(QSize(
                        int(self.movie.scaledSize().width() * self.scale_factor),
                        int(self.movie.scaledSize().height() * self.scale_factor)
                    ))
                    self.pet_image.setMovie(self.movie)
                    self.movie.start()
            if self.status == "free":
                self.free_times += 1
            if self.movie != target_gif:
                self.movie.stop()
                self.movie = target_gif
                self.pet_image.setMovie(self.movie)
                self.movie.start()
            if self.free_times > 20 and self.status == "free":
                self.free_times = 0
                self.status = "busy_2"
                process = mp.Process(target=emotion_assist, daemon=True, args=(self.user_emotion, self.speaker, ))
                process.start()
                self.scene_process = process

    def run(self, frametime:int = 1000//120):
        # 设置动画效果
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(frametime)  # 120 fps

    def animate(self):
        if self.running:  # 新增运行状态检测
            self.global_update()
            self.thread_deleting()
        else:
            self.timer.stop()
                
    def emotion_query(self):
        self.handpose.record(clear=True)
        emotion = self.facial_expression.predict()['result']
        self.user_emotion = emotion
        # try:
        #     emotion = requests.post('http://localhost:8001', json={}, timeout=10).json()['result']
        #     # print("当前情绪：", emotion)
        #     self.user_emotion = emotion
        # except:
        #     pass

    def mousePressEvent(self, event):
        # 鼠标按下时的事件
        self.oldPos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        # 检查是否在宠物图像范围内
        if (self.pet_image.x() <= event.x() <= self.pet_image.x() + self.pet_image.width() and
            self.pet_image.y() <= event.y() <= self.pet_image.y() + self.pet_image.height()):
            pet.hide()  # 隐藏窗口
            setting_window.show()  # 显示设置窗口
            setting_window.raise_()  # 将设置窗口置于最上层:
            self.status = "init"
    

    def mouseMoveEvent(self, event):
        # 判断鼠标在不在pet的范围内
        if event.x() < self.pet_image.x() or event.x() > self.pet_image.x() + self.pet_image.width():
            return
        if event.y() < self.pet_image.y() or event.y() > self.pet_image.y() + self.pet_image.height():
            return
        # 计算鼠标移动的偏移量
        delta = QPoint(event.globalPos() - self.oldPos)
        # 更新窗口位置
        self.pet_image.setGeometry(self.pet_image.x() + delta.x(), self.pet_image.y() + delta.y(), self.pet_image.width(), self.pet_image.height())
        self.slime.x = self.pet_image.x()
        self.slime.y = self.pet_image.y()
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        # 检查是否按下了 Q 键
        if event.key() == Qt.Key_Q:
            self.status = "quit"
            self.close()  # 关闭窗口
            QApplication.quit() 
            sys.exit(0) # 退出整个应用程序
        if event.key() == Qt.Key_C:
            self.status = "init"
            pet.hide()  # 隐藏窗口
            setting_window.show()  # 显示设置窗口
            setting_window.raise_()  # 将设置窗口置于最上层:

    def thread_deleting(self):
        # 删除所有线程
        for thread in self.threads:
            if thread.is_alive():
                continue
            else:
                self.threads.remove(thread)
        if self.scene_process is not None and not self.scene_process.is_alive():
            self.scene_process = None
            self.status = "free"
        if self.talk_process is not None and not self.talk_process.is_alive():
            self.talk_process = None
            self.status = "free"
        if self.game_process is not None and not self.game_process.is_alive():
            self.game_process = None
            self.status = "free"
    
    def __del__(self):
        self.voice_control_process.kill()
        self.voice_control_process.join()
        # 关闭语音识别进程
        self.voice_control_process.close()
        if self.talk_process is not None:
            self.talk_process.kill()
            self.talk_process.join()
        if self.scene_process is not None:
            self.scene_process.kill()
            self.scene_process.join()
        self.thread_deleting()

if __name__ == '__main__':
    # 创建应用实例
    app = QApplication(sys.argv)
    
    QApplication.setStyle('Fusion')  # 设置全局主题（可选 Fusion, Windows 等）

    # 创建并显示设置窗口
    global setting_window
    setting_window = SkinSelectionWindow()
    setting_window.show()

    # 创建并显示桌宠项目主进程
    global pet
    fps = 120
    pet = MyPet(fps=fps)
    pet.setWindowIcon(QIcon('asset/default.png'))
    pet.run(1000//fps)  # 设置帧率
    
    # 连接信号，当设置完成时显示主窗口
    def on_setting_confirmed():
        try:
            setting_window.hide()
            pet.reload_emotion()  # 重新初始化窗口
            pet.status = "free"  # 设置状态为自由
            pet.speaker = setting_window.selected_audio_character
            change_voice(pet.speaker)
            pet.show()  # 显示窗口
            
        except Exception as e:
            print(f"启动失败：{e}")
            setting_window.show() 
    
    setting_window.selection_confirmed.connect(on_setting_confirmed)
    
    # 启动事件循环
    sys.exit(app.exec_())