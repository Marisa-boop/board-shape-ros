import cv2
import numpy as np
import os

# 创建保存图片的文件夹
os.makedirs("square", exist_ok=True)

# 读取A4纸图片
a4_img = cv2.imread("a4_with_border.jpg")
if a4_img is None:
    # 如果找不到文件，则创建一个新的A4图片（含2cm边框）
    A4_WIDTH_MM = 210
    A4_HEIGHT_MM = 297
    DPI = 600  # 打印分辨率

    # 厘米转像素的转换函数
    def cm_to_pixels(cm):
        return int(cm * DPI / 2.54)

    # 计算A4纸像素尺寸
    a4_width = cm_to_pixels(A4_WIDTH_MM / 10)  # 毫米转厘米
    a4_height = cm_to_pixels(A4_HEIGHT_MM / 10)

    # 创建A4图像（白色背景）
    a4_img = np.ones((a4_height, a4_width, 3), dtype=np.uint8) * 255

    # 添加2cm黑色边框
    border_px = cm_to_pixels(2)
    a4_img = cv2.copyMakeBorder(
        a4_img,
        top=border_px,
        bottom=border_px,
        left=border_px,
        right=border_px,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0],  # 黑色边框
    )

# 获取图像中心点
height, width = a4_img.shape[:2]
center_x, center_y = width // 2, height // 2

# 创建不同尺寸的正方形并保存
square_sizes = [10, 11, 12, 13, 14, 15, 16]  # 单位：cm

for size_cm in square_sizes:
    # 复制原始图像
    img_copy = a4_img.copy()

    # 计算正方形边长（像素）
    side_pixels = int(size_cm * 600 / 2.54)  # 600 DPI转换

    # 计算正方形的左上角和右下角坐标
    half_side = side_pixels // 2
    top_left = (center_x - half_side, center_y - half_side)
    bottom_right = (center_x + half_side, center_y + half_side)

    # 绘制黑色实心正方形[7](@ref)
    cv2.rectangle(img_copy, top_left, bottom_right, (0, 0, 0), -1)  # -1表示填充

    # 添加尺寸标注文本
    text = f"{size_cm}cm"
    text_pos = (center_x - 40, center_y + half_side + 30)
    cv2.putText(img_copy, text, text_pos,
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # 保存图片[9,10](@ref)
    filename = f"square/square_{size_cm}cm.jpg"
    cv2.imwrite(filename, img_copy)
    print(f"已保存: {filename}")

print("所有正方形图片已生成并保存到square文件夹")
