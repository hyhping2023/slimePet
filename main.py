import tkinter as tk
from PIL import Image, ImageTk
import time
import os

class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # 去掉窗口边框
        self.root.attributes("-topmost", True)  # 窗口始终在最前端
        self.root.attributes("-transparent", "True")  # 设置透明背景
        # self.root.attributes("-transparentcolor", "white")

        # 窗口位置
        self.x = 0
        self.y = 0
        self.offset_x = 0
        self.offset_y = 0

        # 加载GIF动画
        self.gif_frames = []
        self.load_gif("asset/slime.png")  # 替换为你的GIF文件路径
        self.current_frame = 0

        # 创建画布
        # self.canvas = tk.Canvas(self.root, highlightthickness=0)
        # self.canvas.pack(fill=tk.BOTH, expand=True)
        self.pet_label = tk.Label(self.root, bg="white", highlightthickness=0)
        self.pet_label.pack(fill=tk.NONE)

        # 绑定鼠标事件
        self.pet_label.bind("<ButtonPress-1>", self.start_drag)
        self.pet_label.bind("<B1-Motion>", self.drag)
        self.pet_label.bind("<Double-Button-1>", self.jump)

        # 启动动画
        self.animate()

    def load_image(self, image_path):
        try:
            frame = Image.open(image_path)
            while True:
                frame_rgb = frame.convert("RGBA")
                photo = ImageTk.PhotoImage(frame_rgb)
                self.gif_frames.append(photo)
                try:
                    frame.seek(frame.tell() + 1)
                except EOFError:
                    break
        except Exception as e:
            print(f"Error loading Image: {e}")
            self.gif_frames.append(ImageTk.PhotoImage(Image.new("RGBA", (100, 100), (255, 0, 0, 255))))

    def load_gif(self, gif_path):
        # 加载GIF的每一帧
        try:
            frame = Image.open(gif_path)
            while True:
                frame_rgb = frame.convert("RGBA")
                photo = ImageTk.PhotoImage(frame_rgb)
                self.gif_frames.append(photo)
                try:
                    frame.seek(frame.tell() + 1)
                except EOFError:
                    break
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # 如果没有GIF文件，使用一个简单的静态图像
            self.gif_frames.append(ImageTk.PhotoImage(Image.new("RGBA", (100, 100), (255, 0, 0, 255))))

    def animate(self):
        # 更新GIF动画
        if self.gif_frames:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            # self.canvas.itemconfig(self.pet_image, image=self.gif_frames[self.current_frame])
            self.pet_label.config(image=self.gif_frames[self.current_frame])
        self.root.after(100, self.animate)  # 每100毫秒更新一次

    def start_drag(self, event):
        # 开始拖动
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        # 拖动宠物
        new_x = self.root.winfo_x() + event.x - self.offset_x
        new_y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def jump(self, event):
        # 双击让宠物“跳跃”
        original_y = self.root.winfo_y()
        for i in range(10):
            new_y = original_y - 10 * i
            self.root.geometry(f"+{self.root.winfo_x()}+{new_y}")
            self.root.update()
            time.sleep(0.01)
        for i in range(10):
            new_y = original_y - 100 + 10 * i
            self.root.geometry(f"+{self.root.winfo_x()}+{new_y}")
            self.root.update()
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    pet = DesktopPet(root)
    root.mainloop()