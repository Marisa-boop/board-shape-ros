import cv2
import numpy as np


class HomographyTransformer:
    def __init__(self, homography_matrix=None, src_points=None, dst_points=None):
        """
        初始化单应变换处理器
        :param homography_matrix: 单应矩阵
        :param src_points: 源点坐标
        :param dst_points: 目标点坐标
        :param warp_size: 变换后尺寸
        """
        self.homography = homography_matrix
        self.src_points = np.array(src_points)
        self.dst_points = np.array(dst_points)

        if (
            self.homography is None
            and src_points is not None
            and dst_points is not None
        ):
            self.homography, _ = cv2.findHomography(
                np.array(src_points, dtype=np.float32),
                np.array(dst_points, dtype=np.float32),
                cv2.RANSAC,
            )

    def update_src_points(self, src_points):
        """
        更新源点坐标并重新计算单应矩阵,更新后要recompute_homography
        :param src_points: 新的源点坐标，格式为[[x1,y1], [x2,y2], ...]
        """
        self.src_points = np.array(src_points, dtype=np.float32)
        return self

    def update_dst_points(self, dst_points):
        """
        更新目标点坐标并重新计算单应矩阵,更新后要recompute_homography
        :param dst_points: 新的目标点坐标，格式为[[x1,y1], [x2,y2], ...]
        """
        self.dst_points = np.array(dst_points, dtype=np.float32)
        return self

    def recompute_homography(self):
        """使用当前源点和目标点重新计算单应矩阵"""
        if self.src_points is None or self.dst_points is None:
            return

        # 检查点对数量是否足够（至少4个点）[3,5](@ref)
        if len(self.src_points) < 4 or len(self.dst_points) < 4:
            raise ValueError("至少需要4个点对来计算单应矩阵")

        # 使用RANSAC算法计算单应矩阵，提高鲁棒性[3,7](@ref)
        self.homography, _ = cv2.findHomography(
            self.src_points, self.dst_points, cv2.RANSAC
        )

    def transform_point(self, point):
        """应用单应矩阵变换点坐标

        参数:
            point: 要变换的点，支持多种格式：
                - 单个点 (x, y) 或 [x, y]
                - 点集 [[x1, y1], [x2, y2], ...]
                - numpy数组 (n, 2)

        返回:
            始终返回与输入维度一致的numpy数组：
                - 单点输入 → (1, 2)
                - 多点输入 → (n, 2)
        """
        if self.homography is None:
            return np.array(point) if not isinstance(point, np.ndarray) else point

        # 统一转换为二维数组 (n, 2)
        if isinstance(point, (list, tuple)):
            point = (
                np.array([point])
                if len(point) == 2 and not isinstance(point[0], (list, tuple))
                else np.array(point)
            )
        elif isinstance(point, np.ndarray) and point.ndim == 1:
            point = point.reshape(1, -1)  # 一维转二维

        # 验证形状 (必须为n×2)
        if point.ndim != 2 or point.shape[1] != 2:
            raise ValueError(
                f"Invalid point dimensions. Expected (n, 2), got {point.shape}"
            )

        # 转换为齐次坐标 (x, y, 1)
        point_hom = np.hstack([point, np.ones((point.shape[0], 1))])

        # 应用单应变换
        transformed = np.dot(point_hom, self.homography.T)

        # 齐次坐标转笛卡尔坐标 (x/w, y/w)
        transformed = transformed[:, :2] / transformed[:, 2].reshape(-1, 1)

        return transformed.astype(float)

    # def transform_features(self, features):
    #     """变换特征点集，保持原始形状"""
    #     return self.transform_point(features)
    def transform_features(self, features):
        # 添加输入验证
        if features is None or len(features) == 0:
            return None

        # 确保数据类型正确
        if not isinstance(features, np.ndarray):
            features = np.array(features)

        if features.dtype != np.int32 and features.dtype != np.float32:
            features = features.astype(np.float32)

        return self.transform_point(features)

    # def transform_point(self, point):
    #     """应用单应矩阵变换点坐标"""
    #     if self.homography is None:
    #         return point

    #     point = np.array(point)
    #     if len(point.shape) == 1:
    #         point = point.reshape(1, -1)

    #     point_hom = np.hstack([point, np.ones((point.shape[0], 1))])
    #     transformed = np.dot(point_hom, self.homography.T)
    #     transformed = transformed[:, :2] / transformed[:, 2].reshape(-1, 1)
    #     return transformed.astype(float)
    # def transform_point(self, point):
    #     """应用单应矩阵变换点坐标

    #     参数:
    #         point: 要变换的点，可以是:
    #             - 单个点 (x, y)
    #             - 单个点 [x, y]
    #             - 点集 [[x1, y1], [x2, y2], ...]
    #             - numpy数组 (n, 2)

    #     返回:
    #         变换后的点坐标
    #     """
    #     if self.homography is None:
    #         return point

    #     # 确保点格式统一为numpy数组
    #     if isinstance(point, (list, tuple)):
    #         if len(point) == 2 and not isinstance(point[0], (list, tuple)):
    #             # 处理单个点如 [2.3, 5.4]
    #             point = np.array([point])
    #         else:
    #             # 处理点集如 [[1,2], [3,4]]
    #             point = np.array(point)
    #     elif isinstance(point, np.ndarray) and point.ndim == 1:
    #         # 处理一维numpy数组 [x, y]
    #         if point.shape[0] == 2:
    #             point = point.reshape(1, -1)
    #         else:
    #             raise ValueError(f"Invalid point shape: {point.shape}")

    #     # 点集应具有 (n, 2) 的形状
    #     if point.ndim != 2 or point.shape[1] != 2:
    #         raise ValueError(f"Invalid point dimensions. Expected (n, 2), got {point.shape}")

    #     # 转换为齐次坐标 (x, y, 1)
    #     point_hom = np.hstack([point, np.ones((point.shape[0], 1))])

    #     # 应用单应变换
    #     transformed = np.dot(point_hom, self.homography.T)

    #     # 齐次坐标转换为笛卡尔坐标 (x/w, y/w)
    #     transformed = transformed[:, :2] / transformed[:, 2].reshape(-1, 1)

    #     # 返回格式与输入类型一致
    #     if point.shape[0] == 1:
    #         return transformed[0].astype(float)  # 返回单个点 [x, y]
    #     else:
    #         return transformed.astype(float)  # 返回点集数组

    # def transform_features(self, features):
    #     """变换特征点集"""
    #     return self.transform_point(features)

    def transform_vector_angle(self, vector):
        """变换向量角度"""
        if self.homography is None:
            return vector

        linear_part = self.homography[:2, :2]
        transformed_vector = linear_part @ vector
        return np.degrees(np.arctan2(transformed_vector[1], transformed_vector[0]))

    def warp_frame(
        self,
        src_img,
        dst_size=None,
        flags=cv2.INTER_LINEAR,
        border_mode=cv2.BORDER_CONSTANT,
        border_value=0,
    ):
        """
        应用单应矩阵变换图像并处理负坐标问题
        :param src_img: 输入图像
        :param dst_size: 输出图像尺寸(宽,高)，可选
        :return: 变换后的图像和偏移量信息
        """
        if self.homography is None:
            return src_img.copy(), 0, 0

        # 计算原始图像角点变换后的位置
        h, w = src_img.shape[:2]
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
        transformed_corners = self.transform_point(corners)

        # 计算所有点的最小/最大坐标
        x_min, y_min = np.floor(
            np.min(transformed_corners, axis=0)).astype(int)
        x_max, y_max = np.ceil(np.max(transformed_corners, axis=0)).astype(int)

        # 自动计算输出尺寸（包含负坐标区域）
        width = x_max - x_min
        height = y_max - y_min

        # 创建偏移变换矩阵 - 将整个区域平移到正坐标区
        T_offset = np.array(
            [[1, 0, -x_min], [0, 1, -y_min], [0, 0, 1]], dtype=np.float32
        )

        # 组合单应矩阵和偏移矩阵
        composite_homography = T_offset @ self.homography

        # 执行透视变换（自动调整大小）
        warped_img = cv2.warpPerspective(
            src_img,
            composite_homography,
            (width, height),
            flags=flags,
            borderMode=border_mode,
            borderValue=border_value,
        )

        return warped_img, x_min, y_min
