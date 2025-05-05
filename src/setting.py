from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QRadioButton, QButtonGroup, QFileDialog, QApplication)
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QByteArray, QSize
import os
from asset.drawSlime import EllipseGenerator
from asset.gifcom import GIFBackgroundAdder
from PyQt5.QtGui import QIcon

class SkinSelectionWindow(QWidget):
    selection_confirmed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.movie = None  # 新增movie成员变量
        self.selected_image_path = None  # 初始化属性
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

    def initUI(self):
        self.setWindowTitle('Setting your slime ^w^')
        self.resize(400, 500)
        self.setStyleSheet("background-color: #b9b6d3;")  # 设置整个窗口背景色
        
        # 主布局
        main_layout = QVBoxLayout()
        
        
        # 标题
        title_label = QLabel("Choose default skin or select an image to generate your own skin: ", self)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
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
    
    # def on_skin_selected(self, id):
    #     """处理皮肤选择变化"""
    #     self.upload_btn.setEnabled(id == 1)
    #     if id == 0:  # 默认皮肤
    #         self.movie = None  # 新增movie成员变量
    #         self.update_preview(None)
    
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
    
    def confirm_selection(self):
        """确认选择并启动主程序"""   
        self.close()  # 关闭选择窗口
        self.selection_confirmed.emit()  # 发出信号
        
    def close_app(self):
        """退出程序"""
        self.close()
        # 这里可以添加清理逻辑
        QApplication.quit()
