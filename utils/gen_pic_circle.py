import cv2
import numpy as np
import os

# 创建保存图片的文件夹
os.makedirs("circle", exist_ok=True)

DPI = 600  # 打印分辨率
# 读取A4纸图片
a4_img = cv2.imread("a4_with_border.jpg")
if a4_img is None:
    # 如果文件不存在，则创建新的A4图片（含2cm边框）
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

# 创建不同直径的圆形并保存
diameters_cm = [10, 11, 12, 13, 14, 15, 16]  # 单位：cm

for diameter_cm in diameters_cm:
    # 复制原始图像
    img_copy = a4_img.copy()

    # 计算半径（像素）
    radius_pixels = int((diameter_cm * DPI / 2.54) / 2)  # 厘米转像素后取半

    # 绘制黑色实心圆形
    cv2.circle(
        img_copy, (center_x, center_y), radius_pixels, (0, 0, 0), -1
    )  # -1表示填充

    # 添加尺寸标注文本
    text = f"{diameter_cm}cm"
    text_pos = (center_x - 40, center_y + radius_pixels + 30)
    cv2.putText(img_copy, text, text_pos,
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # 保存图片
    filename = f"circle/circle_{diameter_cm}cm.jpg"
    cv2.imwrite(filename, img_copy)
    print(f"已保存: {filename}")

print("所有圆形图片已生成并保存到circle文件夹")
