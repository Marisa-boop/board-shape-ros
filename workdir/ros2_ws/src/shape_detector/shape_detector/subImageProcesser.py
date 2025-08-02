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

    def extract_rectangular_subimage(self, image, polygon_points):
        """
        提取四边形区域并标准化为256x256，通过顺时针旋转确保方向一致性
        参数:
            image: 输入图像 (numpy数组)
            polygon_points: 四边形点集 [[x1,y1], [x2,y2], ...]
        返回:
            校正后的256x256图像（仅顺时针旋转）
        """
        # 1. 获取有序顶点 [左上, 右上, 右下, 左下]
        rect_points = self.extract_rectangle_features(polygon_points)
        if rect_points is None or len(rect_points) != 4:
            raise ValueError("无法提取有效的四边形顶点")

        # 2. 计算最小外接矩形及其旋转角度 [5,9](@ref)
        rect = cv2.minAreaRect(
            rect_points.reshape(-1, 1, 2).astype(np.float32))
        angle = rect[2]  # OpenCV返回的角度范围为[-90, 0)

        # 3. 角度调整逻辑：确保仅顺时针旋转
        # ------------------------------------------------------------------
        # | 场景                | 原角度 | 调整后角度 | 旋转方向               |
        # |---------------------|--------|------------|-----------------------|
        # | 宽度>高度 (正常矩形) | -90≤θ<0| -θ         | 逆时针转θ→顺时针校正   |
        # | 宽度<高度 (竖矩形)   | -90    | 0°         | 顺时针转90°→水平校正   |
        # ------------------------------------------------------------------
        if angle < -45:  # 处理竖矩形情况
            angle += 90
        else:
            angle = -angle  # 转换为顺时针旋转角度

        # 4. 计算旋转矩阵（顺时针旋转）[10,11](@ref)
        height, width = image.shape[:2]
        M_rotation = cv2.getRotationMatrix2D(
            (width / 2, height / 2), angle, 1.0)

        # 5. 执行旋转（填充透明背景避免裁剪）
        rotated = cv2.warpAffine(
            image,
            M_rotation,
            (width, height),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),  # 黑色填充
        )

        # 6. 提取目标区域（基于旋转后顶点位置）
        # 将原始顶点应用旋转矩阵变换
        ones = np.ones((4, 1))
        homogenous_pts = np.hstack((rect_points, ones))
        rotated_pts = np.dot(homogenous_pts, M_rotation.T)[
            :, :2].astype(np.float32)

        # 7. 单应变换到256x256
        dst_pts = np.array([[0, 0], [255, 0], [255, 255],
                           [0, 255]], dtype=np.float32)
        H, _ = cv2.findHomography(rotated_pts, dst_pts)
        warped = cv2.warpPerspective(
            rotated, H, (256, 256), flags=cv2.INTER_CUBIC)

        return warped

    def extract_rectangle_features(self, contour_points):
        """
        从点集提取矩形顶点（保持不变）
        """
        # 原有实现不变
        points = np.array(contour_points, dtype=np.int32).reshape((-1, 1, 2))
        hull = cv2.convexHull(points)
        if len(hull) < 4:
            return None
        hull_points = hull.reshape(-1, 2)
        if len(hull_points) == 4:
            rect_points = hull_points
        else:
            max_area = 0
            best_points = None
            n = len(hull_points)
            for i in range(n):
                for j in range(i + 1, n):
                    for k in range(j + 1, n):
                        for l in range(k + 1, n):
                            pts = np.array(
                                [
                                    hull_points[i],
                                    hull_points[j],
                                    hull_points[k],
                                    hull_points[l],
                                ]
                            )
                            area = cv2.contourArea(pts)
                            if area > max_area:
                                max_area = area
                                best_points = pts
            rect_points = best_points
        return (
            self._sort_quadrilateral_points(rect_points)
            if rect_points is not None
            else None
        )

    def _sort_quadrilateral_points(self, points):
        """
        顶点排序逻辑（保持不变）
        """
        pts = np.array(points, dtype=np.float32)
        x_sorted = pts[np.argsort(pts[:, 0])]
        left_points = x_sorted[:2]
        right_points = x_sorted[2:]
        left_points = left_points[np.argsort(left_points[:, 1])]
        tl, bl = left_points
        right_points = right_points[np.argsort(right_points[:, 1])]
        tr, br = right_points
        return np.array([tl, tr, br, bl], dtype=np.float32)
