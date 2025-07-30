import cv2
import numpy as np
from .utils import load_points_from_yaml

def undistort_image(frame, camera_matrix_data, dist_coeffs_data):
    """
    应用相机标定参数去除图像畸变
    
    参数:
        image: 原始BGR格式图像
        
    返回:
        校正后的图像
    例如
    camera_matrix_data = np.array([
        [438.783367, 0.000000, 305.593336],
        [0.000000, 437.302876, 243.738352],
        [0.000000, 0.000000, 1.000000]
    ], dtype=np.float32)

    dist_coeffs_data = np.array([-0.361976, 0.110510, 0.001014, 0.000505, 0.000000], 
                                dtype=np.float32)
    """
    return cv2.undistort(
        src=frame,
        cameraMatrix=camera_matrix_data,
        distCoeffs=dist_coeffs_data
    )
camera_matrix_data = np.array([
    [578.87636,   0.     , 327.18428],
    [0.     , 579.65768, 222.19793],
    [ 0.     ,   0.     ,   1.     ]
], dtype=np.float32)

dist_coeffs_data = np.array([0.043851, -0.037104, -0.002796, -0.007263, 0.000000], 
                            dtype=np.float32)
# # 点对需要一一对应
# src_points = np.array(
#     [(139, 220), (437, 278), (283, 248), (318, 145)], dtype=np.float32)
# dst_points = np.array([(346.45, 298.54), (136.45, 292.64),
#                       (241.45, 293), (241.45, 189)], dtype=np.float32)

# 单应变换点对
# src_pts = [
#     (312, 198),
#     (448, 221),
#     (439, 352),
#     (381, 286),
#     (356, 255),
#     (389, 236),
#     (385, 260),
#     (320, 302),
#     (296, 274),
#     (275, 242),
#     (307, 225),
#     (333, 228),
#     (436, 380),
#     (277, 354),
#     (253, 322),
# ]
src_points = load_points_from_yaml("./workdir/ros2_ws/config/src_pts.yaml")
src_points = np.array(src_points, dtype=np.float32)

# dst_points = [
# #     (399.281, -114.632),
# #     (275.460, -99.064),
# #     (292.135, 24.065),
# #     (333.958, -32.421),
#     (357.442, -60.654), # 改
#     (328.325, -80.367),
#     (331.951, -56.576),
# #     (388.145, -13.750),
# #     (410.171, -42.182),
# #     (431.244, -69.940),
# #     (402.807, -91.126),
# #     (379.582, -87.953),
# #     (295.536, 49.85),
# #     (420.113, 32.619),
# #     (442.165, 5.344),
# ]
dst_points = load_points_from_yaml("./workdir/ros2_ws/config/dst_pts.yaml")
dst_points = np.array(dst_points, dtype=np.float32)

# 计算单应矩阵
homography, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC)

print(f"计算出的单应矩阵:\n{homography}")

# 验证单应矩阵的质量
print("\n验证单应矩阵:")
for i, src in enumerate(src_points):
    # 添加齐次坐标(第三维为1)
    pt_hom = np.array([src[0], src[1], 1.0])

    # 正确的矩阵乘法顺序
    dst_calc = homography @ pt_hom  # 单应矩阵(3x3) 乘以 齐次坐标向量(3x1)

    # 转换为二维坐标(除以第三维)
    dst_calc /= dst_calc[2]
    actual_dst = dst_points[i]

    error = np.linalg.norm(dst_calc[:2] - actual_dst)
    print(
        f"源点 {src} => 计算点 {dst_calc[:2].round(2)}, 实际点 {
            actual_dst}, 误差: {error:.4f}"
    )


# 变换点
point_2d = np.array([[262, 30]], dtype=np.float32)  # (x,y)
print(f"\n待变换点: {point_2d[0]}")

# 添加齐次坐标
point_hom = np.hstack((point_2d, np.ones((point_2d.shape[0], 1))))  # (1,3)

# 正确的矩阵乘法顺序
real_coor_hom = np.dot(point_hom, homography.T)  # (1,3) x (3,3) = (1,3)
# 等效写法: homography.dot(point_hom.T).T

# 转换为二维坐标
real_coor = real_coor_hom[:, :2] / real_coor_hom[:, 2].reshape(-1, 1)
print(f"变换后坐标(非齐次): {real_coor[0]}")

# TODO:
#   - x: 480.273
#     y: -76.079
#   - x: 166.0
#     y: 278.0