import cv2
import numpy as np

# A4纸尺寸（单位：毫米）
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297

# 边框宽度（单位：厘米）
BORDER_WIDTH_CM = 2


# 转换函数：厘米转像素（600 DPI打印分辨率）
def cm_to_pixels(cm, dpi=600):
    return int(cm * dpi / 2.54)


# 计算A4纸像素尺寸（600 DPI）
def calculate_a4_pixels(dpi=600):
    width_px = cm_to_pixels(A4_WIDTH_MM / 10, dpi)  # 毫米转厘米后计算
    height_px = cm_to_pixels(A4_HEIGHT_MM / 10, dpi)
    return width_px, height_px


# 计算边框像素大小
border_px = cm_to_pixels(BORDER_WIDTH_CM)

# 创建A4尺寸图像（白色背景）
a4_width, a4_height = calculate_a4_pixels()
a4_image = np.ones((a4_height, a4_width, 3), dtype=np.uint8) * 255  # 白色背景

# 添加黑色边框（使用图像复制填充方式）
bordered_image = cv2.copyMakeBorder(
    a4_image,
    top=border_px,
    bottom=border_px,
    left=border_px,
    right=border_px,
    borderType=cv2.BORDER_CONSTANT,
    value=[0, 0, 0],  # 黑色边框（BGR格式）
)

# 保存结果
cv2.imwrite("a4_with_border.jpg", bordered_image)
print(f"生成成功！图片尺寸：{bordered_image.shape[1]}x{bordered_image.shape[0]}像素")

# 显示结果（按比例缩放显示）
display_scale = 0.2  # 显示缩放比例
display_img = cv2.resize(bordered_image, (0, 0),
                         fx=display_scale, fy=display_scale)
cv2.imshow("A4 with 2cm Border", display_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
