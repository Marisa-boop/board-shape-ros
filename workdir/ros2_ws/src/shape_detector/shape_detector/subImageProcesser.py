import cv2
import numpy as np


# ============================== 子图处理模块 ==============================
class SubImageProcessor:
    def __init__(self):
        self.current_subimages = []

    def extract_subimages(self, frame, detections):
        """从检测结果中提取子图"""
        self.current_subimages = []
        for det in detections:
            subimage = self._extract_subimage(
                frame, det["polygon"], det["xyxy"])
            if subimage is not None:
                # 计算子图坐标系的多边形坐标
                x1, y1, _, _ = map(int, det["xyxy"])
                subimage_polygon = det["polygon"] - [x1, y1]

                # 确保坐标在子图范围内
                h, w = subimage.shape[:2]
                subimage_polygon[:, 0] = np.clip(
                    subimage_polygon[:, 0], 0, w - 1)
                subimage_polygon[:, 1] = np.clip(
                    subimage_polygon[:, 1], 0, h - 1)

                det["subimage"] = subimage
                det["subimage_polygon"] = subimage_polygon
                self.current_subimages.append(subimage)
        return detections

    def _extract_subimage(self, frame, polygon, xyxy):
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [polygon], 255)

        x1, y1, x2, y2 = map(int, xyxy)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

        if x2 <= x1 or y2 <= y1:
            return None

        roi = frame[y1:y2, x1:x2]
        roi_mask = mask[y1:y2, x1:x2]

        bgra = cv2.cvtColor(roi, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = roi_mask
        return bgra

    def get_subimages(self):
        return self.current_subimages

    def restore_coordinates(self, det, points):
        """
        将子图坐标系中的点集还原到原始图像坐标系
        Args:
            det: 检测结果字典（需包含xyxy边界框）
            points: 子图坐标系中的点集，形状为 [N, 2] 的NumPy数组
        Returns:
            原始图像坐标系中的点集，形状为 [N, 2]
        """
        # 提取边界框的左上角坐标
        x1, y1, _, _ = map(int, det["xyxy"])

        # 坐标还原：局部坐标 + 边界框偏移
        restored_points = points + np.array([x1, y1], dtype=points.dtype)

        return restored_points
