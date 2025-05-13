from PIL import Image, ImageSequence

class GIFBackgroundAdder:
    @staticmethod
    def add_background_with_original_speed(gif_path, bg_path, output_path):
        """
        为GIF添加背景并保持原始动画速度
        
        参数:
            gif_path (str): 原始GIF文件路径
            bg_path (str): 背景图片路径
            output_path (str): 输出文件路径
            
        返回:
            bool: 操作是否成功
        """
        try:
            # 加载背景和原GIF
            bg = Image.open(bg_path).convert("RGBA")
            gif = Image.open(gif_path)
        except FileNotFoundError as e:
            print(f"文件未找到: {e}")
            return False
        except Exception as e:
            print(f"发生错误: {e}")
            return False

        frames = []
        delays = []
        
        # 提取原GIF的帧和延迟
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            delays.append(frame.info.get('duration', 100))  # 默认100ms
            # 合成背景
            composite = Image.alpha_composite(bg.copy(), frame)
            frames.append(composite)
        
        try:
            # 保存时保留原延迟
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=delays,
                loop=0
            )
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False