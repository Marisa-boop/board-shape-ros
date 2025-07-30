import cv2
import numpy as np
from typing import Tuple, Optional, List


class PnPSolver:
    """
    使用OpenCV的solvePnP算法进行三维姿态估计的封装类
    功能：根据3D-2D点对应关系计算物体/相机的旋转和平移姿态
    应用场景：增强现实(AR)、机器人定位、三维重建、SLAM初始化等
    """

    def __init__(
        self,
        camera_matrix: np.ndarray,
        dist_coeffs: Optional[np.ndarray] = None,
        method: int = cv2.SOLVEPNP_ITERATIVE,
    ) -> None:
        """
        初始化PnP求解器

        Args:
            camera_matrix (np.ndarray): 3x3相机内参矩阵 [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
            dist_coeffs (np.ndarray): 相机畸变系数 (k1,k2,p1,p2,k3)，默认为None（无畸变）
            method (int): PnP求解算法，支持OpenCV的多种方法[7](@ref):
                          cv2.SOLVEPNP_ITERATIVE (默认) | cv2.SOLVEPNP_EPNP | cv2.SOLVEPNP_P3P
        """
        self.camera_matrix = camera_matrix.astype(np.float32)
        self.dist_coeffs = (
            dist_coeffs if dist_coeffs is not None else np.zeros(
                5, dtype=np.float32)
        )
        self.method = method

        # 验证输入矩阵形状
        if self.camera_matrix.shape != (3, 3):
            raise ValueError("相机内参矩阵必须是3x3数组")

    def solve(
        self, object_points: np.ndarray, image_points: np.ndarray
    ) -> Tuple[bool, np.ndarray, np.ndarray]:
        """
        执行PnP姿态求解

        Args:
            object_points (np.ndarray): N个3D世界坐标点 (N,3) 或 (N,1,3)
            image_points (np.ndarray): 对应的N个2D图像坐标点 (N,2) 或 (N,1,2)

        Returns:
            success (bool): 求解是否成功
            rvec (np.ndarray): 旋转向量 (3,1)
            tvec (np.ndarray): 平移向量 (3,1)

        Raises:
            ValueError: 输入点数量不足或维度错误
        """
        # 输入验证和预处理
        op = np.asarray(object_points, dtype=np.float32).reshape(-1, 1, 3)
        ip = np.asarray(image_points, dtype=np.float32).reshape(-1, 1, 2)

        if len(op) < 4 and self.method != cv2.SOLVEPNP_P3P:
            raise ValueError(
                f"至少需要4个点对（当前：{len(op)}），P3P算法仅需3个点[5](@ref)"
            )

        return cv2.solvePnP(
            objectPoints=op,
            imagePoints=ip,
            cameraMatrix=self.camera_matrix,
            distCoeffs=self.dist_coeffs,
            flags=self.method,
        )

    @staticmethod
    def rotation_vector_to_matrix(rvec: np.ndarray) -> np.ndarray:
        """将旋转向量转换为3x3旋转矩阵[6](@ref)"""
        return cv2.Rodrigues(rvec)[0]

    @staticmethod
    def calculate_reprojection_error(
        object_points: np.ndarray,
        image_points: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
    ) -> float:
        """
        计算重投影误差（像素误差）[7](@ref)

        Args:
            object_points: 3D世界坐标点
            image_points: 实际观测的2D图像点
            rvec, tvec: 求解得到的姿态参数
            camera_matrix, dist_coeffs: 相机参数

        Returns:
            mean_error (float): 平均重投影误差（像素）
        """
        # 投影3D点
        projected_points, _ = cv2.projectPoints(
            object_points, rvec, tvec, camera_matrix, dist_coeffs
        )

        # 计算欧氏距离
        errors = np.linalg.norm(
            projected_points.reshape(-1, 2) - image_points, axis=1)
        return float(np.mean(errors))

    def visualize_pose(
        self,
        image: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray,
        object_axes: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        在图像上绘制姿态坐标系（可视化X/Y/Z轴）

        Args:
            image: 原始BGR图像
            rvec, tvec: 求解得到的姿态
            object_axes: 自定义坐标系端点 (4x3数组)，默认为单位坐标系

        Returns:
            带姿态坐标系的图像
        """
        if object_axes is None:
            # 默认坐标系：原点 + 三个轴端点 (单位：米)
            object_axes = np.array(
                [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, -1]], dtype=np.float32
            )

        # 投影坐标系到图像平面
        axis_points, _ = cv2.projectPoints(
            object_axes, rvec, tvec, self.camera_matrix, self.dist_coeffs
        )
        axis_points = axis_points.reshape(-1, 2).astype(int)

        # 绘制坐标轴
        origin = tuple(axis_points[0])
        cv2.line(image, origin, tuple(
            axis_points[1]), (0, 0, 255), 3)  # X轴 (红色)
        cv2.line(image, origin, tuple(
            axis_points[2]), (0, 255, 0), 3)  # Y轴 (绿色)
        cv2.line(image, origin, tuple(
            axis_points[3]), (255, 0, 0), 3)  # Z轴 (蓝色)
        return image


if __name__ == "__main__":
    # 1. 初始化相机参数 (需提前标定获得)
    camera_matrix = np.array(
        [[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32
    )
    dist_coeffs = np.array([0.1, -0.2, 0, 0, 0.1], dtype=np.float32)  # 畸变系数

    # 2. 创建PnP求解器实例
    pnp_solver = PnPSolver(camera_matrix, dist_coeffs,
                           method=cv2.SOLVEPNP_EPNP)

    # 3. 准备3D-2D对应点 (示例数据)
    object_points = np.array(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32
    )  # 世界坐标 (米)
    image_points = np.array(
        [[320, 240], [400, 240], [320, 300], [300, 200]], dtype=np.float32
    )  # 像素坐标

    # 4. 求解姿态
    success, rvec, tvec = pnp_solver.solve(object_points, image_points)

    if success:
        # 5. 结果解析
        rotation_matrix = PnPSolver.rotation_vector_to_matrix(rvec)
        reproj_error = PnPSolver.calculate_reprojection_error(
            object_points, image_points, rvec, tvec, camera_matrix, dist_coeffs
        )

        print(f"旋转向量: {rvec.flatten()}")
        print(f"平移向量: {tvec.flatten()} (米)")
        print(f"重投影误差: {reproj_error:.2f} 像素")

        # 6. 可视化 (需有图像输入)
        # img_with_pose = pnp_solver.visualize_pose(img.copy(), rvec, tvec)
        # cv2.imshow("Pose Visualization", img_with_pose)
    else:
        print("PnP求解失败！检查输入点对或算法选择")
