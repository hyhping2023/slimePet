from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QApplication, QComboBox)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QSize
import os
from .drawSlime import EllipseGenerator
from .gifcom import GIFBackgroundAdder
from PyQt5.QtGui import QIcon
import sys
from .config import NAME2REALNAME, AVAIABLE_VOICES


if not os.path.exists("asset/DIY"):
    os.makedirs("asset/DIY")

class SkinSelectionWindow(QWidget):
    selection_confirmed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.movie = None  # 新增movie成员变量
        self.selected_image_path = None  # 初始化属性
        self.selected_audio = None  # 存储选中的音频文件
        self.selected_audio_character = "anno"  # 默认选中的音频角色
        self.initUI()
        self.img=[
            "asset/default/DEFAULT_smile.gif",
            "asset/default/DEFAULT_aww.gif",
            "asset/default/DEFAULT_cool.gif",
            "asset/default/DEFAULT_cute.gif",
            "asset/default/DEFAULT_nauseated.gif",
            "asset/default/DEFAULT_worried.gif"
        ] 

        self.setWindowIcon(QIcon('asset/default.png'))
    
    def showEvent(self, event):
        """窗口显示时加载默认预览"""
        super().showEvent(event)
        self.update_preview(None)  # 现在加载预览
        self.load_audio_files()  # 加载音频文件

    def initUI(self):
        self.setWindowTitle('Setting your slime ^w^')
        self.resize(400, 500)
        self.setStyleSheet("background-color: #b9b6d3; font-family: Kristen ITC; ")  # 设置整个窗口背景色
        
        # 主布局
        main_layout = QVBoxLayout()
        
        
        # 标题
        title_label = QLabel("Choose default skin or select an image to generate your own skin: ", self)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; font-family: Kristen ITC; ")
        main_layout.addWidget(title_label)
        

        # 皮肤选择选项
        btn_layout = QHBoxLayout()
        
        # Default 按钮
        default_btn = QPushButton("Default", self)
        default_btn.clicked.connect(self.use_default)  # 直接绑定到方法
        
        # Upload 按钮
        upload_btn = QPushButton("Upload", self)
        upload_btn.clicked.connect(self.upload_image)  # 直接绑定到方法
        
        btn_layout.addWidget(default_btn)
        btn_layout.addWidget(upload_btn)
        main_layout.addLayout(btn_layout)
        
        # 图片预览区域
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        main_layout.addWidget(self.preview_label)

         # 音频选择部分
        audio_layout = QVBoxLayout()
        
        # 音频选择标签
        audio_label = QLabel("Select voice model:", self)
        audio_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        audio_layout.addWidget(audio_label)
        
        # 音频下拉菜单
        self.audio_combo = QComboBox(self)
        self.audio_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
        """)
        self.audio_combo.currentIndexChanged.connect(self.on_audio_selected)
        audio_layout.addWidget(self.audio_combo)
        
        main_layout.addLayout(audio_layout)
        
        # 确认和退出按钮
        buttons_layout = QHBoxLayout()
        
        self.confirm_btn = QPushButton("Confirm", self)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        buttons_layout.addWidget(self.confirm_btn)
        
        exit_btn = QPushButton("Quit", self)
        exit_btn.clicked.connect(self.close_app)
        buttons_layout.addWidget(exit_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    

    def use_default(self):
        """使用默认皮肤"""
        self.img = [
            "asset/default/DEFAULT_smile.gif",
            "asset/default/DEFAULT_aww.gif",
            "asset/default/DEFAULT_cool.gif",
            "asset/default/DEFAULT_cute.gif",
            "asset/default/DEFAULT_nauseated.gif",
            "asset/default/DEFAULT_worried.gif"
        ] 
        self.selected_image_path = None
        self.update_preview(None)

    def upload_image(self):
        """打开文件对话框选择图片"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择皮肤图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)", 
            options=options
        )
        
        if file_path:
            self.selected_image_path = file_path
            try:
                EllipseGenerator.create_average_sampled_ellipse(
                    width=22, 
                    height=22, 
                    sample_image_path=file_path, 
                    output_path= "asset/DIY/skin.png"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/smile.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/smile.gif"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/aww.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/aww.gif"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/cool.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/cool.gif"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/cute.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/cute.gif"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/nauseated.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/nauseated.gif"
                )

                GIFBackgroundAdder.add_background_with_original_speed(
                    "asset/expressions/worried.gif", 
                    "asset/DIY/skin.png", 
                    "asset/DIY/worried.gif"
                )
                self.img=[
                    "asset/DIY/smile.gif",
                    "asset/DIY/aww.gif",
                    "asset/DIY/cool.gif",
                    "asset/DIY/cute.gif",
                    "asset/DIY/nauseated.gif",
                    "asset/DIY/worried.gif"
                ]
                self.update_preview(self.img[0])  # 显示第一个GIF
            except Exception as e:
                print(f"处理图片时出错: {e}")
                return
             
    def update_preview(self, image_path):
        """更新预览区域"""
        if self.movie:
            self.movie.stop()
            self.preview_label.clear()
        if image_path is None:
            # 加载默认GIF
            self.movie = QMovie(self.img[0])
        else:
            # 加载处理后的GIF
            self.movie = QMovie(image_path)
            
        # 设置GIF显示参数
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setScaledSize(QSize(200, 200))
        self.preview_label.setMovie(self.movie)
        self.movie.start()
    
    def load_audio_files(self):
        audio_dir = "asset/voice/model"
        """加载voice/model文件夹中的wav音频文件"""
        # print("Loading audio files...")
        if not os.path.exists(audio_dir):
            # os.makedirs(audio_dir)
            print(f"Audio directory {audio_dir} not found")
            return
        
        # 获取所有.wav文件
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
        
        # 清空并重新填充下拉菜单
        self.audio_combo.clear()
        
        if not audio_files:
            self.audio_combo.addItem("No audio files found")
            self.audio_combo.setEnabled(False)
            return
        
        self.audio_combo.addItem("Select a voice model...")
        # 添加音频文件项，使用NAME2REALNAME中的对应名称
        for audio_file in audio_files:
            # 去掉.wav后缀
            base_name = os.path.splitext(audio_file)[0]
            # 查找对应的友好名称
            display_name = NAME2REALNAME.get(base_name, base_name)
            # 添加到下拉菜单，存储原始文件名作为用户数据
            self.audio_combo.addItem(display_name, userData=audio_file)
        self.audio_combo.setCurrentIndex(0)
    
    def on_audio_selected(self, index):
        """处理音频选择变化"""
        if index > 0:  # 跳过第一个提示项
            selected_key = self.audio_combo.currentData()  # 获取存储的key值
            display_text = self.audio_combo.currentText()  # 获取当前显示的文本
            
            # 立即更新下拉菜单显示
            self.audio_combo.setCurrentIndex(index)
            self.selected_audio = selected_key  # 存储选中的key
            self.selected_audio_character = selected_key.replace(".wav", "")  # 去掉.wav后缀
            
            # 构建完整的wav文件路径
            wav_path = "asset/voice/model/"+selected_key
            
            # 播放音频（使用线程避免阻塞UI）
            if sys.platform == "win32":
                import winsound
                import threading
                def play_sound():
                    try:
                        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                    except:
                        print("error")
                threading.Thread(target=play_sound).start()
            else:
                from pydub import AudioSegment
                from pydub.playback import play
                import threading
                def play_sound():
                    try:
                        song = AudioSegment.from_wav(wav_path)
                        play(song)
                    except:
                        print("error")
                threading.Thread(target=play_sound).start()

    def confirm_selection(self):
        """确认选择并启动主程序"""   
        self.close()  # 关闭选择窗口
        self.selection_confirmed.emit()  # 发出信号
        
    def close_app(self):
        """退出程序"""
        self.close()
        # 这里可以添加清理逻辑
        QApplication.quit()


if __name__ == '__main__':
    # 创建应用实例
    app = QApplication(sys.argv)
    
    QApplication.setStyle('Fusion')  # 设置全局主题（可选 Fusion, Windows 等）

    # 创建并显示设置窗口
    global setting_window
    setting_window = SkinSelectionWindow()
    setting_window.show()
    
    # 连接信号，当设置完成时显示主窗口
    def on_setting_confirmed():
        setting_window.hide()
        print("exit")
    
    setting_window.selection_confirmed.connect(on_setting_confirmed)

    # 启动应用程序事件循环
    sys.exit(app.exec_())