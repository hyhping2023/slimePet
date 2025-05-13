from PIL import Image

def process_pixel_art_with_alpha(width, height, input_path, output_path):
    # 1. 打开图片（保持RGBA模式）
    
    try:
        img = Image.open(input_path).convert('RGBA')  # 确保是RGBA模式
    except FileNotFoundError:
        print("错误：图片不存在！")
        return
    except Exception as e:
        print(f"打开图片错误: {e}")
        return

    # 2. 检查是否为110x110
    if img.size != (110, 110):
        print(f"警告：图片尺寸不是110x110（当前尺寸: {img.size}）")

    # 3. 压缩到22x22（特殊处理透明通道）
    def box_resample_with_alpha(image, size):
        """自定义重采样方法，正确处理透明像素"""
        result = Image.new('RGBA', size)
        for y in range(size[1]):
            for x in range(size[0]):
                # 计算源图像中5x5区域
                src_x = x * 5
                src_y = y * 5
                box = (src_x, src_y, src_x+5, src_y+5)
                
                # 提取区域内的像素
                region = image.crop(box)
                pixels = region.getdata()
                
                # 计算平均颜色（考虑透明度）
                total_r = total_g = total_b = total_a = 0
                count = 0
                for r, g, b, a in pixels:
                    if a > 0:  # 只计算非完全透明像素
                        total_r += r
                        total_g += g
                        total_b += b
                        total_a += a
                        count += 1
                
                # 设置结果像素
                if count > 0:
                    avg_r = int(total_r / count)
                    avg_g = int(total_g / count)
                    avg_b = int(total_b / count)
                    avg_a = int(total_a / count)
                    result.putpixel((x, y), (avg_r, avg_g, avg_b, avg_a))
                else:
                    result.putpixel((x, y), (0, 0, 0, 0))  # 完全透明
        return result

    small_img = box_resample_with_alpha(img, (22, 22))

    

    if width and height:
        try:
            width = int(width)
            height = int(height)
            # 使用NEAREST保持硬边缘
            scaled_img = small_img.resize((width, height), Image.NEAREST)
        except ValueError:
            print("错误：尺寸必须是整数，将保持22x22")
            scaled_img = small_img
    else:
        scaled_img = small_img

    # 5. 放大5倍（保持像素风格）
    final_img = scaled_img.resize(
        (scaled_img.width * 5, scaled_img.height * 5), 
        Image.NEAREST
    )

    # 保存结果（PNG格式保留透明度）
    final_img.save(output_path, 'PNG')
    print(f"处理完成！保存到 {output_path}")
    print(f"最终尺寸: {final_img.size}")
    print("注意：已保留透明度通道")

# # 运行
# process_pixel_art_with_alpha()
input_path = input("输入图片路径: ")

for i in range(-3,4):
    width = 22+i
    height = 22-i
    output_path = f"default_{width}x{height}.png"

    process_pixel_art_with_alpha(width, height, input_path, output_path)
    