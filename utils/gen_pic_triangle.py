import cv2
import numpy as np
import os

# 创建保存图片的文件夹
os.makedirs("triangle", exist_ok=True)

# A4纸尺寸（毫米）和DPI设置
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
DPI = 600  # 打印分辨率


# 厘米转像素的转换函数
def cm_to_pixels(cm):
    return int(cm * DPI / 2.54)


# 计算A4纸像素尺寸
def calculate_a4_pixels():
    width_px = cm_to_pixels(A4_WIDTH_MM / 10)  # 毫米转厘米
    height_px = cm_to_pixels(A4_HEIGHT_MM / 10)
    return width_px, height_px


# 读取A4纸图片
a4_img = cv2.imread("a4_with_border.jpg")
if a4_img is None:
    # 如果找不到文件，则创建一个新的A4图片
    a4_width, a4_height = calculate_a4_pixels()
    a4_img = np.ones((a4_height, a4_width, 3), dtype=np.uint8) * 255  # 白色背景

# 获取图像中心点
height, width = a4_img.shape[:2]
center_x, center_y = width // 2, height // 2

# 创建不同尺寸的三角形并保存
triangle_sizes = [10, 11, 12, 13, 14, 15, 16]  # 单位：cm

for size_cm in triangle_sizes:
    # 复制原始图像
    img_copy = a4_img.copy()

    # 计算三角形边长（像素）
    side_pixels = cm_to_pixels(size_cm)

    # 计算等边三角形高度（像素）
    height_pixels = int(np.sqrt(3) / 2 * side_pixels)

    # 计算三个顶点坐标[6](@ref)
    top = (center_x, center_y - height_pixels // 2)
    bottom_left = (center_x - side_pixels // 2, center_y + height_pixels // 2)
    bottom_right = (center_x + side_pixels // 2, center_y + height_pixels // 2)

    # 创建三角形顶点数组[3](@ref)
    triangle_pts = np.array([top, bottom_left, bottom_right], np.int32)
    triangle_pts = triangle_pts.reshape((-1, 1, 2))

    # 绘制黑色实心三角形[3](@ref)
    cv2.fillPoly(img_copy, [triangle_pts], color=(0, 0, 0))

    # 添加尺寸标注文本
    text = f"{size_cm}cm"
    cv2.putText(
        img_copy,
        text,
        (center_x - 30, center_y + height_pixels // 2 + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    # 保存图片[9](@ref)
    filename = f"triangle/triangle_{size_cm}cm.jpg"
    cv2.imwrite(filename, img_copy)
    print(f"已保存: {filename}")

print("所有三角形图片已生成并保存到triangle文件夹")
