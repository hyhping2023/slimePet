from PIL import Image, ImageTk
import time, os
import random

types = {
    0: "surprise",
    1: "angry",
    2: "happy",
    3: "sad",
    4: "neutral",
}

class DesktopPet:
    def __init__(self, size, screen_width, screen_height):
        # 初始化桌面属性
        self.screen_width = screen_width
        self.screen_height = screen_height
        # 位置相关属性
        self.x = screen_width // 2
        self.y = screen_height // 2
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

        # 情感
        self.emotion = 'neutral'

        # 运动速度相关
        self.speed_threshold = 300  # 速度阈值（像素/秒）
        self.high_speed_start_time = 0  # 开始高速运动的时间
        self.high_speed_duration = 0.5  # 需要保持高速运动的时间
        
        # 碰撞相关
        self.collision_count = 0  # 当前运动周期内的碰撞次数
        self.last_collision_time = 0  # 上次碰撞时间
        self.collision_reset_time = 5  # 碰撞状态重置时间（秒）
        
        # 状态标志
        self.is_high_speed = False  # 是否处于高速状态
        self.is_nauseated = False  # 是否处于眩晕状态
    

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

    def change_emotion(self, user_emotion):
        if user_emotion != self.emotion:
            if random.random() < 0.8: # 80%概率改变情感
                self.emotion = user_emotion
                print(f"情感变化为: {self.emotion}")
                return True
            self.emotion = user_emotion
        else:
            if random.random() < 0.1: # 10%概率改变情感
                new_emotion = random.choice(list(types.values()))
                if new_emotion != self.emotion:
                    self.emotion = new_emotion
                    print(f"情感变化为: {self.emotion}")
                    return True
        return False    

    def update(self,):
        # 更新宠物位置和显示
        current_time = time.time()
        delta_time = current_time - self.last_time
        
        if not self.is_grabbed:  # 只有在没有被抓住时才应用物理效果
            # 应用速度衰减
            self.velocity_x *= 0.99  # 衰减系数
            self.velocity_y *= 0.99
            
            # 如果速度很小，直接停止
            if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                self.velocity_x = 0
                self.velocity_y = 0
            
            # 计算当前速度
            current_speed = ((self.velocity_x**2 + self.velocity_y**2)**0.5)
            
            # 检测碰撞
            if (self.x <= 0 or self.x >= self.screen_width - self.size or 
                self.y <= 0 or self.y >= self.screen_height - self.size):
                if current_time - self.last_collision_time > 0.1:  # 防重复计数
                    self.collision_count += 1
                    self.last_collision_time = current_time

            # 检测高速状态
            if current_speed > self.speed_threshold:
                if not self.is_high_speed:
                    self.high_speed_start_time = current_time
                    self.is_high_speed = True
            else:
                if self.is_high_speed:
                    # 检查是否需要进入眩晕状态
                    if self.collision_count >= 3 and not self.is_nauseated:
                        self.is_nauseated = True
                        self.nauseated_start_time = current_time
                    self.is_high_speed = False
                    self.collision_count = 0  # 重置碰撞计数

            # 检查眩晕状态是否结束
            if self.is_nauseated and current_time - self.nauseated_start_time > self.collision_reset_time:
                self.is_nauseated = False

            # 更新位置
            if delta_time > 0.001:  # 防止除零错误
                self.x += self.velocity_x * delta_time
                self.y += self.velocity_y * delta_time
                if self.x < 0:
                    self.x = 0
                    self.velocity_x = -self.velocity_x * 0.5  # 反弹
                elif self.x > self.screen_width - self.size:
                    self.x = self.screen_width - self.size
                    self.velocity_x = -self.velocity_x * 0.5  # 反弹
                    
                if self.y < 0:
                    self.y = 0
                    self.velocity_y = -self.velocity_y * 0.5  # 反弹
                elif self.y > self.screen_height - self.size:
                    self.y = self.screen_height - self.size
                    self.velocity_y = -self.velocity_y * 0.5  # 反弹
        
        
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
