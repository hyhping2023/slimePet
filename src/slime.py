from PIL import Image, ImageTk
import tkinter as tk
import time, os

class DesktopPet:
    def __init__(self, root: tk.Tk, size = 110):
        self.root = root
        self.root.overrideredirect(True)  # 去掉窗口边框
        self.root.attributes("-topmost", True)  # 窗口始终在最前端
        if os.name == 'nt':
            self.root.attributes("-transparentcolor", "white") # Windows透明色  
        else:  
            self.root.attributes("-transparent", "True")  # 设置透明背景
        

        # 窗口位置
        self.x = self.root.winfo_screenwidth() // 2
        self.y = self.root.winfo_screenheight() // 2
        self.root.geometry(f"+{self.x}+{self.y}")
        self.offset_x = 0
        self.offset_y = 0
        self.size = size

        # 加载帧
        self.frames = []
        self.frames.extend(self.load_image("asset/slime.png"))  # 替换为你的GIF文件路径
        self.current_frame = 0

        # 创建画布
        self.pet_label = tk.Label(self.root, bg="white", highlightthickness=0)
        self.pet_label.pack(fill=tk.NONE)
        self.pet_label.config(width=self.size, height=self.size)

        # 绑定鼠标事件
        self.pet_label.bind("<ButtonPress-1>", self.start_drag)
        self.pet_label.bind("<B1-Motion>", self.drag)
        self.pet_label.bind("<Double-Button-1>", self.jump)

        # # 导入表情图片
        # self.emotions = {
        #     "smile": ImageTk.PhotoImage(Image.open("asset/smile.png").convert("RGBA")),
        #     "sad": ImageTk.PhotoImage(Image.open("asset/sad.png").convert("RGBA")),
        #     # "angry": ImageTk.PhotoImage(Image.open("asset/angry.png").convert("RGBA")),
        # }

        # 启动动画
        self.animate()

    def load_image(self, image_path):
        frames = []
        try:
            image = Image.open(image_path).resize((self.size, self.size), resample=Image.BICUBIC)
            image_rgb = image.convert("RGBA")
            photo = ImageTk.PhotoImage(image_rgb)
            frames.append(photo)
            try:
                image.seek(image.tell() + 1)
            except EOFError:
                pass
        except Exception as e:
            print(f"Error loading Image: {e}")
            frames.append(ImageTk.PhotoImage(Image.new("RGBA", (self.size, self.size), (255, 0, 0, 255))))
        return frames
    
    def load_gif(self, gif_path):
        # 加载GIF的每一帧
        frames = []
        try:
            frame = Image.open(gif_path).resize((self.size, self.size), resample=Image.LANCZOS)
            while True:
                frame_rgb = frame.convert("RGBA")
                photo = ImageTk.PhotoImage(frame_rgb)
                frames.append(photo)
                try:
                    frame.seek(frame.tell() + 1)
                except EOFError:
                    break
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # 如果没有GIF文件，使用一个简单的静态图像
            frames.append(ImageTk.PhotoImage(Image.new("RGBA", (100, 100), (255, 0, 0, 255))))
        return frames
    
    def animate(self, emotion="smile"):
        # 更新图片
        if self.frames:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            # self.canvas.itemconfig(self.pet_image, image=self.gif_frames[self.current_frame])
            self.pet_label.config(image=self.frames[self.current_frame])
                
        # self.root.after(16, self.animate)  # 每100毫秒更新一次

    def start_drag(self, event):
        # 开始拖动
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        # 拖动宠物
        new_x = self.root.winfo_x() + event.x - self.offset_x
        new_y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{new_x}+{new_y}")
        self.x, self.y = new_x, new_y

    def update(self):
        # 更新宠物位置
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

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