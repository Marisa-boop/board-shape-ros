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

    def extract_rectangular_subimage(self, image, polygon_points, aspect_ratio=None):
        """
        提取四边形区域并标准化为256x256
        参数:
            image: 输入图像 (numpy数组)
            polygon_points: 四边形点集 [[x1,y1], [x2,y2], ...]
            aspect_ratio: 保留参数但不使用
        返回:
            256x256标准化图像
        """
        # 1. 点集转换为四边形顶点
        rect_points = self.extract_rectangle_features(polygon_points)
        if rect_points is None or len(rect_points) != 4:
            raise ValueError("无法提取有效的四边形顶点")

        # 2. 顶点排序（左上->右上->右下->左下）
        sorted_pts = self._sort_quadrilateral_points(rect_points)

        # 3. 定义目标顶点（256x256）
        dst_pts = np.array([[0, 0], [255, 0], [255, 255],
                           [0, 255]], dtype=np.float32)

        # 4. 计算单应变换矩阵
        H, _ = cv2.findHomography(sorted_pts, dst_pts)

        # 5. 应用透视变换
        warped = cv2.warpPerspective(
            image, H, (256, 256), flags=cv2.INTER_CUBIC
        )  # 使用高质量插值[4](@ref)

        return warped

    def extract_rectangle_features(self, contour_points):
        """
        从点集提取矩形顶点
        参数:
            contour_points: 点集 [[x1,y1], [x2,y2], ...]
        返回:
            四边形顶点坐标 [左上, 右上, 右下, 左下]
        """
        # 转换为凸包[3,5](@ref)
        points = np.array(contour_points, dtype=np.int32).reshape((-1, 1, 2))
        hull = cv2.convexHull(points)

        if len(hull) < 4:
            return None

        # 提取凸包点并转换为(n,2)格式
        hull_points = hull.reshape(-1, 2)

        # 若凸包点数为4，直接使用
        if len(hull_points) == 4:
            rect_points = hull_points
        else:
            # 寻找面积最大的四边形顶点组合[3](@ref)
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
        将四边形顶点排序为: 左上->右上->右下->左下
        基于:
          1. 按x坐标排序
          2. 分为左侧点和右侧点
          3. 分别按y坐标排序
        """
        pts = np.array(points, dtype=np.float32)

        # 按x坐标排序[7](@ref)
        x_sorted = pts[np.argsort(pts[:, 0])]

        # 分为左侧点和右侧点
        left_points = x_sorted[:2]
        right_points = x_sorted[2:]

        # 左侧点按y排序：y小→左上，y大→左下
        left_points = left_points[np.argsort(left_points[:, 1])]
        tl, bl = left_points  # tl=左上, bl=左下

        # 右侧点按y排序：y小→右上，y大→右下
        right_points = right_points[np.argsort(right_points[:, 1])]
        tr, br = right_points  # tr=右上, br=右下

        return np.array([tl, tr, br, bl], dtype=np.float32)
