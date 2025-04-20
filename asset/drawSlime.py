from PIL import Image, ImageDraw
import numpy as np
import colorsys

def create_average_sampled_ellipse(width, height, sample_image_path, output_path, scale=5, darkness=0.7):
    # 打开采样图片并转换为numpy数组
    try:
        sample_img = Image.open(sample_image_path).convert('RGB')
        sample_array = np.array(sample_img)
    except:
        print("无法打开采样图片，请检查路径")
        return
    
    # 计算整张图片的平均颜色
    avg_color = tuple(np.mean(sample_array, axis=(0, 1)).astype(int))

    # 转换为HSV并降低亮度
    r, g, b = [x/255.0 for x in avg_color]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v = max(0, v * darkness)  # darkness参数控制亮度降低程度
    dark_r, dark_g, dark_b = colorsys.hsv_to_rgb(h, s, v)
    outline_color = (int(dark_r*255), int(dark_g*255), int(dark_b*255), 255)

    # 创建目标图像（原始大小）
    target_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(target_img)
    
    # 计算椭圆参数
    center_x = (width - 1) / 2
    center_y = (height - 1) / 2
    a = (width - 1) / 2  # 水平半径
    b = (height - 1) / 2  # 垂直半径
    
    sample_height, sample_width, _ = sample_array.shape
    
    # 预计算椭圆内所有点
    ellipse_points = []
    for y in range(height):
        for x in range(width):
            x0 = x - center_x
            y0 = y - center_y
            if (x0/a)**2 + (y0/b)**2 <= 1:
                ellipse_points.append((x, y, x0, y0))
    
    # 计算每个椭圆内像素对应的采样区域
    for x, y, x0, y0 in ellipse_points:
        # 计算采样区域边界（在采样图片上的范围）
        left = int(((x0 + a) / (2 * a)) * sample_width)
        top = int(((y0 + b) / (2 * b)) * sample_height)
        
        # 定义采样区域大小（可根据需要调整）
        sample_size = 5  # 采样5x5区域
        half_size = sample_size // 2
        
        # 计算实际采样区域
        x1 = max(0, left - half_size)
        y1 = max(0, top - half_size)
        x2 = min(sample_width - 1, left + half_size)
        y2 = min(sample_height - 1, top + half_size)
        
        # 计算区域平均色
        region = sample_array[y1:y2+1, x1:x2+1]
        if region.size == 0:
            avg_color = (128, 128, 128)  # 默认灰色
        else:
            avg_color = tuple(np.mean(region, axis=(0, 1)).astype(int))
        
        # 填充像素
        draw.point((x, y), (*avg_color, 255))
    

    

    # 绘制椭圆轮廓（黑色）
    for y in range(height):
        for x in range(width):
            x0 = x - center_x
            y0 = y - center_y
            
            if abs(x0) <= a:
                yp = b * (1 - (x0/a)**2)**0.5
                if abs(abs(y0) - yp) <= 0.5:
                    draw.point((x, y), outline_color)
            
            if abs(y0) <= b:
                xp = a * (1 - (y0/b)**2)**0.5
                if abs(abs(x0) - xp) <= 0.5:
                    draw.point((x, y), outline_color)
    
    # 放大图像（保持像素化效果）
    scaled_size = (width * scale, height * scale)
    scaled_img = target_img.resize(scaled_size, Image.NEAREST)
    
    # 保存结果
    scaled_img.save(output_path, 'PNG')
    print(f"已保存平均采样填充的像素椭圆到: {output_path}")

# # 示例使用
# width = int(input("请输入椭圆的宽度(像素): "))
# height = int(input("请输入椭圆的高度(像素): "))
# sample_image = input("请输入采样图片路径: ")
# output_filename = f"avg_sampled_ellipse_{width}x{height}_scaled.png"

# create_average_sampled_ellipse(width, height, sample_image, output_filename)
sample_image = input("请输入采样图片路径: ")
for i in range(-3,4):
    width = 22+i
    height = 22-i
    
    output_filename = f"{width}x{height}.png"

    create_average_sampled_ellipse(width, height, sample_image, output_filename)

