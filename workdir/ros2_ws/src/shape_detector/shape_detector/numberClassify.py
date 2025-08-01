import cv2
import numpy as np
from ultralytics import YOLO


class NumberClassifier:
    def __init__(self, model_path="yolov8n-cls.pt", conf_threshold=0.1, device="auto"):
        """
        数字分类器初始化
        :param model_path: 预训练模型路径（支持.pt或.onnx格式）
        :param conf_threshold: 置信度阈值（低于此值视为无效预测）
        :param device: 推理设备（'cpu', 'cuda' 或 'auto'自动选择）
        """
        # 加载模型并强制转换为float32精度[6](@ref)
        self.model = YOLO(model_path).float(
        ) if device == "cpu" else YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.device = device
        self.class_names = {i: str(i) for i in range(10)}  # 数字0-9的类别映射

    def detect(self, image):
        """
        执行数字分类推理
        :param image: 输入图像 (支持文件路径或numpy数组)
        :return: (predicted_digit, confidence) 元组 (若无有效预测返回None)
        """
        # 支持文件路径输入[5](@ref)
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise ValueError(f"无法读取图像: {image}")

        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.model(image, verbose=False)

        # 后处理 - 提取概率最高的类别
        if results and hasattr(results[0], "probs"):
            probs = results[0].probs.data.cpu().numpy()
            top1_index = np.argmax(probs)
            confidence = probs[top1_index]

            if confidence >= self.conf_threshold:
                result = int(self.class_names[top1_index]), float(confidence)
                return result
        return None

    def visualize(self, frame, number):
        """
        在图像左上角可视化识别结果（精简版）
        :param frame: 输入图像 (numpy数组)
        :param number: 要显示的数字 (整数)
        :return: 带标注结果的图像
        """
        # 将数字转换为字符串
        text = str(number)

        # 获取图像尺寸
        height, width = frame.shape[:2]

        # 设置精简字体参数
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0  # 减小字体大小[5](@ref)
        thickness = 2  # 减小线条粗细
        color = (0, 255, 0)  # 绿色(BGR格式)

        # 获取文本尺寸
        (text_width, text_height), _ = cv2.getTextSize(
            text, font, font_scale, thickness
        )

        # 设置左上角位置（保留适当边距）
        x = 10
        y = text_height + 20

        # 添加简洁背景框提高可读性
        bg_top_left = (x - 5, y - text_height - 5)
        bg_bottom_right = (x + text_width + 5, y + 5)
        cv2.rectangle(
            frame, bg_top_left, bg_bottom_right, (0, 0, 0), -1  # 黑色背景  # 填充矩形
        )

        # 在左上角绘制数字[7](@ref)
        cv2.putText(
            frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA
        )

        return frame

    # def visualize(self, frame, number):
    #     """
    #     在图像中心可视化识别结果
    #     :param frame: 输入图像 (numpy数组)
    #     :param number: 要显示的数字 (整数)
    #     :return: 带标注结果的图像
    #     """
    #     # 将数字转换为字符串
    #     text = str(number)
    #
    #     # 获取图像尺寸
    #     height, width = frame.shape[:2]
    #
    #     # 设置字体参数
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     font_scale = 3  # 字体大小[4](@ref)
    #     thickness = 4  # 线条粗细
    #     color = (0, 255, 0)  # 绿色(BGR格式)[4](@ref)
    #
    #     # 获取文本尺寸和基线[5](@ref)
    #     (text_width, text_height), baseline = cv2.getTextSize(
    #         text, font, font_scale, thickness
    #     )
    #
    #     # 计算居中位置[5](@ref)
    #     x = (width - text_width) // 2
    #     y = (height + text_height) // 2  # 垂直居中
    #
    #     # 添加半透明背景提高可读性[5](@ref)
    #     bg_margin = 20
    #     bg_top_left = (x - bg_margin, y - text_height - bg_margin)
    #     bg_bottom_right = (x + text_width + bg_margin, y + bg_margin)
    #     overlay = frame.copy()
    #     cv2.rectangle(overlay, bg_top_left, bg_bottom_right,
    #                   (0, 0, 0), -1)  # 黑色背景
    #     frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)  # 60%透明度
    #
    #     # 在图像中心绘制数字[4](@ref)
    #     cv2.putText(
    #         frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA
    #     )
    #
    #     # 添加外框增强视觉效果
    #     cv2.rectangle(
    #         frame,
    #         (x - 10, y - text_height - 10),
    #         (x + text_width + 10, y + 10),
    #         (0, 200, 255),  # 橙黄色边框
    #         2,  # 边框厚度
    #     )
    #
    #     return frame
