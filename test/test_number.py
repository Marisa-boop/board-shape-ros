import cv2
import numpy as np
from ultralytics import YOLO
import torch

class NumberClassifier:
    def __init__(self, model_path="yolov8n-cls.pt", conf_threshold=0.5, device="auto"):
        """
        数字分类器初始化
        :param model_path: 预训练模型路径（支持.pt或.onnx格式）
        :param conf_threshold: 置信度阈值（低于此值视为无效预测）
        :param device: 推理设备（'cpu', 'cuda' 或 'auto'自动选择）
        """
        # 加载模型并强制转换为float32精度[6](@ref)
        self.model = YOLO(model_path).float() if device == "cpu" else YOLO(model_path)
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
        
        # 统一转换为RGB格式[9](@ref)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 关键修复：直接传递原始图像，禁用手动预处理[9](@ref)
        results = self.model(image, 
                            verbose=False, 
                            device=self.device,
                            imgsz=224  # 指定输入尺寸[2](@ref)
        )

        # 后处理 - 提取概率最高的类别
        if results and hasattr(results[0], "probs"):
            probs = results[0].probs.data.cpu().numpy()
            top1_index = np.argmax(probs)
            confidence = probs[top1_index]
            
            if confidence >= self.conf_threshold:
                return int(self.class_names[top1_index]), float(confidence)
        return None

    def visualize(self, image, prediction=None):
        """
        可视化分类结果（调试用）
        :param image: 原始输入图像
        :param prediction: detect()的返回结果
        :return: 带标注结果的图像
        """
        display_img = image.copy()
        if prediction is not None:
            digit, conf = prediction
            label = f"Digit: {digit} ({conf:.2f})"
            cv2.putText(
                display_img,
                label,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        return display_img

# 使用示例
if __name__ == "__main__":
    print("torch cuda: ", torch.cuda.is_available())
    # 初始化分类器
    number_classifier = NumberClassifier(model_path="workdir/ros2_ws/model/number.pt")
    
    # 示例1：处理图像文件
    result = number_classifier.detect("assets/test_number.jpg")
    print(f"识别结果: {result}")