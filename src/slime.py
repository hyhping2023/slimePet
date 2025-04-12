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

        # 速度相关属性
        self.velocity_x = 0
        self.velocity_y = 0
        self.last_x = self.x
        self.last_y = self.y
        self.last_time = time.time()
        self.is_grabbed = False  # 是否被手势抓住

        # 位置历史记录
        self.position_history = []  # 存储最近的位置和时间
        self.history_length = 5  # 记录最近5个位置点
        self.sample_interval = 0.05  # 采样间隔（秒）

        # 冷却时间相关属性
        self.cooldown_time = 0.5  # 冷却时间（秒）
        self.last_release_time = 0  # 上次释放时间
        self.last_collision_time = 0  # 上次碰撞时间
        self.is_in_cooldown = False  # 是否在冷却中
        self.grab_cooldown_time = 0.3  # 抓取冷却时间（秒）
        self.last_grab_time = 0  # 上次抓取时间

        # 形变相关属性
        self.deformation = 1.0  # 当前形变比例
        self.target_deformation = 1.0  # 目标形变比例
        self.deformation_direction = 0  # 形变方向（0: 无, 1: 水平, 2: 垂直）
        self.deformation_speed = 0.5  # 形变恢复速度
        self.max_deformation = 0.5  # 最大形变程度

        # 加载原始图像
        self.original_image = Image.open("asset/slime.png")
        self.original_photo = ImageTk.PhotoImage(self.original_image.resize((self.size, self.size), Image.BICUBIC))
        
        # 创建画布
        self.pet_label = tk.Label(self.root, bg="white", highlightthickness=0)
        self.pet_label.pack(fill=tk.NONE)
        self.pet_label.config(width=self.size, height=self.size)
        self.pet_label.config(image=self.original_photo)

        # 加载帧
        self.frames = []
        self.frames.extend(self.load_image("asset/slime.png"))  # 替换为你的GIF文件路径
        self.current_frame = 0

        # 绑定鼠标事件
        self.pet_label.bind("<ButtonPress-1>", self.start_drag)
        self.pet_label.bind("<B1-Motion>", self.drag)
        self.pet_label.bind("<ButtonRelease-1>", self.stop_drag)
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
            self.pet_label.config(image=self.frames[self.current_frame])
                
        # 继续动画
        self.root.after(100, self.animate)  # 每100毫秒更新一次

    def start_drag(self, event):
        # 检查是否在冷却中
        current_time = time.time()
        if current_time - self.last_grab_time < self.grab_cooldown_time:
            return
        
        # 开始拖动
        self.offset_x = event.x
        self.offset_y = event.y
        self.is_grabbed = True
        self.drag_start_time = time.time()
        self.drag_start_x = self.x
        self.drag_start_y = self.y
        self.velocity_x = 0
        self.velocity_y = 0
        self.last_time = time.time()  # 重置最后时间

    def update_position_history(self, x, y, current_time):
        # 更新位置历史记录
        self.position_history.append((x, y, current_time))
        if len(self.position_history) > self.history_length:
            self.position_history.pop(0)

    def calculate_velocity(self):
        if len(self.position_history) < 2:
            return 0, 0
        
        # 计算总位移和时间
        total_dx = 0
        total_dy = 0
        total_time = 0
        
        for i in range(1, len(self.position_history)):
            x1, y1, t1 = self.position_history[i-1]
            x2, y2, t2 = self.position_history[i]
            total_dx += x2 - x1
            total_dy += y2 - y1
            total_time += t2 - t1
        
        if total_time > 0:
            return total_dx / total_time, total_dy / total_time
        return 0, 0

    def drag(self, event):
        # 拖动宠物
        new_x = self.root.winfo_x() + event.x - self.offset_x
        new_y = self.root.winfo_y() + event.y - self.offset_y
        
        # 更新位置历史
        current_time = time.time()
        self.update_position_history(new_x, new_y, current_time)
        
        # 计算速度
        self.velocity_x, self.velocity_y = self.calculate_velocity()
        
        self.x, self.y = new_x, new_y
        self.update()  # 使用update方法更新位置和显示

    def stop_drag(self, event):
        self.is_grabbed = False
        # 使用历史记录计算最终速度
        self.velocity_x, self.velocity_y = self.calculate_velocity()
        
        # 限制最大速度
        max_speed = 2000  # 增加最大速度限制
        self.velocity_x = max(min(self.velocity_x, max_speed), -max_speed)
        self.velocity_y = max(min(self.velocity_y, max_speed), -max_speed)
        
        # 设置抓取冷却时间
        self.last_grab_time = time.time()
        
        # 清空位置历史
        self.position_history.clear()

    def update(self):
        # 更新宠物位置和显示
        current_time = time.time()
        delta_time = current_time - self.last_time
        
        if not self.is_grabbed:  # 只有在没有被抓住时才应用物理效果
            # 应用速度衰减
            self.velocity_x *= 0.95  # 衰减系数
            self.velocity_y *= 0.95
            
            # 如果速度很小，直接停止
            if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                self.velocity_x = 0
                self.velocity_y = 0
            
            # 更新位置
            if delta_time > 0.001:  # 防止除零错误
                self.x += self.velocity_x * delta_time
                self.y += self.velocity_y * delta_time
                
                # 边界检查
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                if self.x < 0:
                    self.x = 0
                    self.velocity_x = -self.velocity_x * 0.5  # 反弹
                elif self.x > screen_width - self.size:
                    self.x = screen_width - self.size
                    self.velocity_x = -self.velocity_x * 0.5  # 反弹
                    
                if self.y < 0:
                    self.y = 0
                    self.velocity_y = -self.velocity_y * 0.5  # 反弹
                elif self.y > screen_height - self.size:
                    self.y = screen_height - self.size
                    self.velocity_y = -self.velocity_y * 0.5  # 反弹
        
        # 更新显示
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.pet_label.config(image=self.frames[self.current_frame])
        
        # 更新最后位置和时间
        self.last_x, self.last_y = self.x, self.y
        self.last_time = current_time

    def set_position(self, x, y):
        # 计算速度
        current_time = time.time()
        delta_time = current_time - self.last_time
        if delta_time > 0.001:  # 防止除零错误
            self.velocity_x = (x - self.last_x) / delta_time
            self.velocity_y = (y - self.last_y) / delta_time
        
        # 更新位置
        self.x = x
        self.y = y

    def set_grabbed(self, grabbed):
        self.is_grabbed = grabbed

    def jump(self, event):
        # 双击让宠物"跳跃"
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