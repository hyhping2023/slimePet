from PIL import Image, ImageSequence

def add_background_with_original_speed(gif_path, bg_path, output_path):
    try:
        # 加载背景和原GIF
        bg = Image.open(bg_path).convert("RGBA")
    except:
        print("cannot find"+bg_path)

    try:
        gif = Image.open(gif_path)
    except:
        print("cannot find"+gif_path)


    frames = []
    delays = []
    
    # 提取原GIF的帧和延迟
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        delays.append(frame.info.get('duration', 100))  # 默认100ms
        # 合成背景
        composite = Image.alpha_composite(bg.copy(), frame)
        frames.append(composite)
    
    # print(delays)


    # 保存时保留原延迟
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=delays,  # 关键：使用原延迟
        loop=0           # 无限循环
    )

# 调用示例
add_background_with_original_speed("nauseated.gif", "default.png", "nauseated0.gif")