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

    def extract_rectangular_subimage(self, subimg, polygon, aspect_ratio=2.0):
        """
        从检测到的方形区域中提取长方形子图（旋转矩形区域）

        参数:
            subimg: 原始子图 (BGRA格式)
            polygon: 子图坐标系中的多边形点集
            aspect_ratio: 长方形宽高比 (默认2:1)

        返回:
            校正后的长方形图像 (BGRA格式)
        """
        # 1. 计算最小外接旋转矩形
        rect = cv2.minAreaRect(polygon)
        center, size, angle = rect

        # 2. 根据宽高比调整矩形尺寸
        width, height = size
        if width < height:
            width, height = height, width
            angle += 90  # 旋转角度

        # 根据宽高比调整尺寸
        new_height = min(width, height)
        new_width = new_height * aspect_ratio
        size = (new_width, new_height)

        # 3. 获取旋转矩形的四个角点
        box = cv2.boxPoints((center, size, angle))
        box = np.int0(box)

        # 4. 对点集排序（左上、右上、右下、左下）
        ordered_box = self._order_points(box)

        # 5. 计算目标尺寸（保持原始分辨率）
        max_dim = max(subimg.shape[0], subimg.shape[1])
        dst_width = int(max_dim * 0.8)  # 保留80%原始尺寸
        dst_height = int(dst_width / aspect_ratio)

        # 6. 定义目标点（透视变换后的位置）
        dst_pts = np.array(
            [
                [0, 0],
                [dst_width - 1, 0],
                [dst_width - 1, dst_height - 1],
                [0, dst_height - 1],
            ],
            dtype="float32",
        )

        # 7. 计算透视变换矩阵
        M = cv2.getPerspectiveTransform(
            ordered_box.astype(np.float32), dst_pts)

        # 8. 应用透视变换
        warped = cv2.warpPerspective(
            subimg,
            M,
            (dst_width, dst_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0),  # 透明背景
        )

        return warped

    @staticmethod
    def _order_points(pts):
        """将点排序为（左上，右上，右下，左下）顺序"""
        # 初始化坐标矩阵
        rect = np.zeros((4, 2), dtype="float32")

        # 计算中心点
        center = np.mean(pts, axis=0)

        # 按角度排序点
        angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
        sorted_pts = pts[np.argsort(angles)]

        # 识别左上、右上、右下、左下
        x_sorted = sorted_pts[np.argsort(sorted_pts[:, 0])]
        y_sorted = sorted_pts[np.argsort(sorted_pts[:, 1])]

        leftmost = x_sorted[:2]
        rightmost = x_sorted[2:]

        rect[0] = leftmost[np.argmin(leftmost[:, 1])]  # 左上
        rect[1] = rightmost[np.argmin(rightmost[:, 1])]  # 右上
        rect[2] = rightmost[np.argmax(rightmost[:, 1])]  # 右下
        rect[3] = leftmost[np.argmax(leftmost[:, 1])]  # 左下

        return rect
