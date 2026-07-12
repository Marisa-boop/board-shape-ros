# Copyright (c) 2025 Marisa-boop
# SPDX-License-Identifier: MIT

import cv2
import numpy as np


class GeometryFeatureProcessor:
    def __init__(self):
        """初始化几何特征处理器"""
        self.reference_short_edge = None
        self.reference_long_edge = None
        self.gray_image = None

    # def extract_rectangle_features(self, contour):
    #     # """提取长方形特征 - 四个顶点"""
    #     # rect = cv2.minAreaRect(contour)
    #     # box = cv2.boxPoints(rect)
    #     # return box.astype(np.int32)
    #     """提取方形特征 - 四个顶点"""
    #     epsilon = 0.04 * cv2.arcLength(contour, True)
    #     approx = cv2.approxPolyDP(contour, epsilon, True)
    #     if len(approx) == 4:
    #         return approx.reshape(4, 2)
    #     else:
    #         rect = cv2.minAreaRect(contour)
    #         return np.float64(cv2.boxPoints(rect))

    # def extract_board_features(self, contour):
    # if len(contour) < 4 :
    #     return None
    # epsilon = 0.04 * cv2.arcLength(contour, True)
    # approx = cv2.approxPolyDP(contour, epsilon, True)
    # if len(approx) == 4:
    #     return approx.reshape(4, 2)
    # else:
    #     rect = cv2.minAreaRect(contour)
    #     return np.float64(cv2.boxPoints(rect))
    # """提取板子特征 - 四个顶点"""
    # rect = cv2.minAreaRect(contour)
    # box = cv2.boxPoints(rect)
    # return box.astype(np.int32)
    # """提取方形特征 - 四个顶点"""
    # epsilon = 0.04 * cv2.arcLength(contour, True)
    # approx = cv2.approxPolyDP(contour, epsilon, True)
    # if len(approx) == 4:
    #     return approx.reshape(4, 2)
    # else:
    #     rect = cv2.minAreaRect(contour)
    #     return np.float64(cv2.boxPoints(rect))
    # ===== 1. 初步轮廓过滤 =====
    # if len(contour) < 4 :
    #     return None

    # # ===== 2. 凸包逼近 (精度提升关键) =====
    # hull = cv2.convexHull(contour)
    # epsilon = 0.001 * cv2.arcLength(hull, True)  # 动态精度系数
    # approx = cv2.approxPolyDP(hull, epsilon, True)

    # # 顶点数量验证
    # if len(approx) == 4:
    #     return approx.reshape(4, 2)
    # else:
    #     rect = cv2.minAreaRect(hull)
    #     return np.float64(cv2.boxPoints(rect))
    def extract_board_features(self, contour):
        if len(contour) < 4:
            return None

        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            points = approx.reshape(4, 2)
        else:
            rect = cv2.minAreaRect(contour)
            points = np.float64(cv2.boxPoints(rect))

        # ===== 新增排序逻辑 =====
        # 按x+y的和排序，找到左上角和右下角（左上角和右下角是四个点中坐标值相加后分别最小和最大的点）
        # 如果存在多个点具有相同的最小或最大 x+y 值，则以 x 坐标排序
        sum_coords = np.sum(points, axis=1)
        # 左上角：x+y 最小的点，如果有并列，取 x 较小的点
        tl_idx = np.argmin(sum_coords)
        # 右下角：x+y 最大的点，如果有并列，取 x 较大的点
        br_idx = np.argmax(sum_coords)

        # 剩余的两个点
        remaining_idxs = [i for i in range(4) if i not in [tl_idx, br_idx]]

        # 根据 x 坐标区分左下角和右上角
        # 左下角：x 坐标较小的点（属于剩余两个点中 x 坐标较小的那个）
        if points[remaining_idxs[0]][0] < points[remaining_idxs[1]][0]:
            bl_idx = remaining_idxs[0]
            tr_idx = remaining_idxs[1]
        else:
            bl_idx = remaining_idxs[1]
            tr_idx = remaining_idxs[0]

        # 验证排序结果：确保左上角的 y 值小于左下角，右上角的 y 值小于右下角
        if points[tl_idx][1] > points[bl_idx][1]:
            tl_idx, bl_idx = bl_idx, tl_idx
        if points[tr_idx][1] > points[br_idx][1]:
            tr_idx, br_idx = br_idx, tr_idx

        # 按标准顺序返回点: 左上→左下→右下→右上
        return np.array(
            [points[tl_idx], points[bl_idx], points[br_idx], points[tr_idx]]
        )

    # be youhuad
    # def extract_square_features(self, contour):
    #     """提取方形特征 - 返回四个有序角点和平均边长
    #     Args:
    #         contour: 输入轮廓
    #     Returns:
    #         corners: 排序后的四个角点 [左上, 右上, 右下, 左下]
    #         avg_side: 平均边长
    #     """
    #     # === 新增：轮廓有效性验证 ===
    #     if contour is None or len(contour) < 4:
    #         return None, None
    #
    #     # === 修复1：确保轮廓数据类型正确 ===
    #     if contour.dtype != np.float32:
    #         try:
    #             # 转换为OpenCV要求的32位浮点型
    #             contour = contour.astype(np.float32)
    #         except:
    #             return None, None
    #
    #     # === 修复2：添加异常捕获 ===
    #     try:
    #         # 1. 多边形逼近
    #         epsilon = 0.04 * cv2.arcLength(contour, True)
    #         approx = cv2.approxPolyDP(contour, epsilon, True)
    #     except Exception as e:
    #         print(f"轮廓处理异常: {str(e)}")
    #         return None, None
    #
    #     # 2. 获取四个顶点
    #     if len(approx) == 4:
    #         corners = approx.reshape(4, 2)
    #     else:
    #         try:
    #             rect = cv2.minAreaRect(contour)
    #             corners = np.float32(cv2.boxPoints(rect))  # 确保输出为float32
    #         except:
    #             return None, None
    #
    #     # 3. 角点排序（左上→右上→右下→左下）
    #     def sort_corners(pts):
    #         # 按x坐标排序
    #         x_sorted = pts[np.argsort(pts[:, 0])]
    #         # 分为左右两组
    #         left_pts = x_sorted[:2]
    #         right_pts = x_sorted[2:]
    #         # 左侧按y排序（上→下）
    #         left_pts = left_pts[np.argsort(left_pts[:, 1])]
    #         # 右侧按y排序（上→下）
    #         right_pts = right_pts[np.argsort(right_pts[:, 1])]
    #         return np.array([left_pts[0], right_pts[0], right_pts[1], left_pts[1]])
    #
    #     try:
    #         sorted_corners = sort_corners(corners)
    #     except:
    #         return None, None
    #
    #     # 4. 计算各边长度
    #     side_lengths = []
    #     for i in range(4):
    #         p1 = sorted_corners[i]
    #         p2 = sorted_corners[(i + 1) % 4]
    #         side_lengths.append(np.linalg.norm(p1 - p2))
    #
    #     # 5. 计算平均边长
    #     avg_side = np.mean(side_lengths)
    #
    #     return sorted_corners, avg_side

    def extract_square_features(self, contour):
        """高精度提取方形特征 - 亚像素级角点定位+最小二乘优化
        Args:
            contour: 输入轮廓 (N,1,2)
        Returns:
            corners: 优化后的四个角点 [左上, 右上, 右下, 左下]
            avg_side: 亚像素级平均边长
        """
        # ===== 1. 轮廓预处理 =====
        if contour is None or len(contour) < 4:
            return None, None

        # 转换为浮点型并移除重复点
        contour = contour.astype(np.float32).reshape(-1, 2)
        contour = np.unique(contour, axis=0)

        # 计算凸包保证凸性
        hull = cv2.convexHull(contour.reshape(-1, 1, 2)).reshape(-1, 2)
        if len(hull) < 4:
            return None, None

        # ===== 2. 顶点初始化 =====
        # 最小外接矩形获取初始顶点
        rect = cv2.minAreaRect(hull.reshape(-1, 1, 2))
        init_corners = cv2.boxPoints(rect).astype(np.float32)

        # 顶点排序函数
        def sort_corners(pts):
            # 按x坐标排序
            x_sorted = pts[np.argsort(pts[:, 0])]
            # 左边两点按y排序
            left_pts = x_sorted[:2][np.argsort(x_sorted[:2, 1])]
            # 右边两点按y排序
            right_pts = x_sorted[2:][np.argsort(x_sorted[2:, 1])]
            return np.vstack([left_pts[0], right_pts[0], right_pts[1], left_pts[1]])

        sorted_corners = sort_corners(init_corners)

        # ===== 3. 亚像素级顶点优化 =====
        if hasattr(self, "gray_image") and self.gray_image is not None:
            # 对每个角点进行亚像素优化
            win_size = 5  # 减小窗口尺寸
            criteria = (cv2.TERM_CRITERIA_EPS +
                        cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

            for i in range(len(sorted_corners)):
                pt = sorted_corners[i].reshape(1, 1, 2).astype(np.float32)
                try:
                    cv2.cornerSubPix(
                        self.gray_image, pt, (win_size,
                                              win_size), (-1, -1), criteria
                    )
                    sorted_corners[i] = pt[0][0]
                except cv2.error:
                    # 安全处理边界错误
                    continue

        # ===== 4. 精确角点计算 =====
        # 使用最小二乘法优化直线拟合
        def fit_line(points):
            """最小二乘拟合直线"""
            x = points[:, 0]
            y = points[:, 1]
            A = np.vstack([x, np.ones(len(x))]).T
            m, c = np.linalg.lstsq(A, y, rcond=None)[0]
            return m, -1, c  # ax + by + c = 0 (b = -1)

        optimized_corners = []
        for i in range(4):
            # 确定每条边的点集区域
            p1, p2 = sorted_corners[i], sorted_corners[(i + 1) % 4]

            # 选择属于当前边的轮廓点
            edge_points = []
            for pt in hull:
                # 点到直线距离 + 投影位置判断
                vec1 = (p2 - p1).flatten()
                vec2 = (pt - p1).flatten()
                cross = np.abs(np.cross(vec1, vec2))
                dot = np.dot(vec2, vec1)

                if cross < np.linalg.norm(vec1) and 0 <= dot <= np.dot(vec1, vec1):
                    edge_points.append(pt)

            if len(edge_points) > 2:
                # 最小二乘拟合直线
                m, b, c = fit_line(np.array(edge_points))
                optimized_corners.append((m, b, c))
            else:
                # 点不足时使用初始边
                vec = p2 - p1
                normal = np.array([-vec[1], vec[0]])
                normal /= np.linalg.norm(normal)
                optimized_corners.append(
                    (normal[0], normal[1], -np.dot(normal, p1)))

        # ===== 5. 角点计算与边长 =====
        final_corners = []
        for i in range(4):
            # 解两条直线的交点
            a1, b1, c1 = optimized_corners[i]
            a2, b2, c2 = optimized_corners[(i + 1) % 4]

            try:
                # 解线性方程组
                A = np.array([[a1, b1], [a2, b2]])
                b_vec = np.array([-c1, -c2])
                corner = np.linalg.solve(A, b_vec)
                final_corners.append(corner)
            except:
                # 退化情况使用初始角点
                final_corners.append(sorted_corners[i])

        final_corners = np.array(final_corners)

        # ===== 6. 边长计算 =====
        side_lengths = []
        for i in range(4):
            p1 = final_corners[i]
            p2 = final_corners[(i + 1) % 4]
            side_lengths.append(np.linalg.norm(p2 - p1))

        avg_side = np.mean(side_lengths)

        return sort_corners(final_corners), avg_side

    # be youhuad
    # def extract_square_features(self, contour):
    #     """提取方形特征 - 四个顶点"""
    #     if len(contour) < 4:
    #         return None
    #     epsilon = 0.04 * cv2.arcLength(contour, True)
    #     approx = cv2.approxPolyDP(contour, epsilon, True)
    #     if len(approx) == 4:
    #         return approx.reshape(4, 2)
    #     else:
    #         rect = cv2.minAreaRect(contour)
    #         return np.float64(cv2.boxPoints(rect))

    # # # ===== 2. 凸包逼近 (精度提升关键) =====
    # # hull = cv2.convexHull(contour)
    # # epsilon = 0.001 * cv2.arcLength(hull, True)  # 动态精度系数
    # approx = cv2.approxPolyDP(hull, epsilon, True)

    # # 顶点数量验证
    # if len(approx) == 4:
    #     return approx.reshape(4, 2)
    # else:
    #     rect = cv2.minAreaRect(contour)
    #     return np.float64(cv2.boxPoints(rect))

    # def extract_rectangle_features(self, contour):
    #     """提取矩形特征 - 优化顶点提取和顺时针排序"""
    #     # 计算轮廓的凸包
    #     hull = cv2.convexHull(contour)
    #
    #     if len(hull) < 4:
    #         return None
    #
    #     # 提取凸包点并转换为(n,2)格式
    #     hull_points = hull.reshape(-1, 2)
    #
    #     # 若凸包点数为4，直接使用
    #     if len(hull_points) == 4:
    #         rect_points = hull_points
    #     else:
    #         # 寻找面积最大的四边形顶点组合
    #         max_area = 0
    #         best_points = None
    #         n = len(hull_points)
    #
    #         for i in range(n):
    #             for j in range(i + 1, n):
    #                 for k in range(j + 1, n):
    #                     for l in range(k + 1, n):
    #                         pts = np.array(
    #                             [
    #                                 hull_points[i],
    #                                 hull_points[j],
    #                                 hull_points[k],
    #                                 hull_points[l],
    #                             ]
    #                         )
    #                         area = cv2.contourArea(pts)
    #                         if area > max_area:
    #                             max_area = area
    #                             best_points = pts
    #         rect_points = best_points
    #
    #     if rect_points is None:
    #         return None
    #
    #     # 对顶点进行顺时针排序：左上→右上→右下→左下
    #     def sort_points(points):
    #         # 1. 按x坐标排序
    #         x_sorted = points[np.argsort(points[:, 0])]
    #         # 2. 分为左侧点和右侧点
    #         left_points = x_sorted[:2]
    #         right_points = x_sorted[2:]
    #         # 3. 左侧点按y排序：y小→左上，y大→左下
    #         left_points = left_points[np.argsort(left_points[:, 1])]
    #         tl, bl = left_points  # tl=左上, bl=左下
    #         # 4. 右侧点按y排序：y小→右上，y大→右下
    #         right_points = right_points[np.argsort(right_points[:, 1])]
    #         tr, br = right_points  # tr=右上, br=右下
    #         return np.array([tl, tr, br, bl])
    #
    #     return sort_points(rect_points)

    def extract_rectangle_features(self, contour):
        """
        高精度提取矩形顶点（亚像素级优化）
        参数:
            contour: 输入轮廓 [N, 1, 2]
        返回:
            顺时针排序的四边形顶点 [左上, 右上, 右下, 左下]
        """
        # 1. 轮廓预处理
        if contour is None or len(contour) < 4:
            return None

        # 转换为浮点格式
        contour_f = contour.astype(np.float32).reshape(-1, 1, 2)

        # 2. 多边形逼近
        epsilon = 0.015 * cv2.arcLength(contour_f, True)
        approx = cv2.approxPolyDP(contour_f, epsilon, True)

        # 3. 顶点数量处理
        if len(approx) < 4:
            hull = cv2.convexHull(contour_f)
            if len(hull) < 4:
                return None
            approx = hull

        # 4. 亚像素级优化（安全执行）
        if hasattr(self, "gray_image") and self.gray_image is not None:
            win_size = 5  # 减小窗口尺寸[1](@ref)
            criteria = (cv2.TERM_CRITERIA_EPS +
                        cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

            try:
                # 检查所有点是否在安全边界内
                margin = win_size * 2 + 5
                valid_points = []
                for pt in approx:
                    x, y = pt[0]
                    if (
                        margin < x < self.gray_image.shape[1] - margin
                        and margin < y < self.gray_image.shape[0] - margin
                    ):
                        valid_points.append(True)
                    else:
                        valid_points.append(False)

                # 只优化安全点
                if all(valid_points):
                    cv2.cornerSubPix(
                        self.gray_image,
                        approx,
                        (win_size, win_size),
                        (-1, -1),
                        criteria,
                    )
            except cv2.error:
                # 安全处理OpenCV错误
                pass

        # 5. 最小外接矩形精确拟合
        rect = cv2.minAreaRect(approx)
        rect_points = cv2.boxPoints(rect).astype(np.float32)

        # 6. 顶点排序优化
        # 计算质心
        centroid = np.mean(rect_points, axis=0)

        # 计算相对向量的极角
        vectors = rect_points - centroid
        angles = np.arctan2(vectors[:, 1], vectors[:, 0])

        # 按角度排序
        sorted_idx = np.argsort(angles)

        # 顺时针排序 [左上, 右上, 右下, 左下]
        return rect_points[sorted_idx]

    # def extract_rectangle_features(self, contour):
    #     """提取征 - 使用面积最大法优化顶点提取"""
    #     # 计算轮廓的凸包
    #     hull = cv2.convexHull(contour)
    #
    #     if len(hull) < 4:
    #         return None
    #
    #     if len(hull) == 4:
    #         return hull.reshape(4, 2)
    #
    #     max_area = 0
    #     best_points = None
    #
    #     for i in range(len(hull)):
    #         for j in range(i + 1, len(hull)):
    #             for k in range(j + 1, len(hull)):
    #                 for l in range(k + 1, len(hull)):
    #                     # 获取点
    #                     pts = np.array(
    #                         [hull[i][0], hull[j][0], hull[k][0], hull[l][0]])
    #
    #                     # 计算面积
    #                     area = cv2.contourArea(pts)
    #
    #                     # 记录最大面积
    #                     if area > max_area:
    #                         max_area = area
    #                         best_points = pts
    #
    #     return best_points
    # """
    # 超高精度矩形特征提取算法

    # 参数:
    #     contour: 输入的轮廓点集 (Nx2数组)
    # 返回:
    # """
    # # ===== 1. 初步轮廓过滤 =====
    # if len(contour) < 4 :
    #     return None

    # # ===== 2. 凸包逼近 (精度提升关键) =====
    # hull = cv2.convexHull(contour)
    # epsilon = 0.001 * cv2.arcLength(hull, True)  # 动态精度系数
    # approx = cv2.approxPolyDP(hull, epsilon, True)

    # # 顶点数量验证
    # if len(approx) == 4:
    #     return approx.reshape(4, 2)
    # else:
    #     rect = cv2.minAreaRect(hull)
    #     return np.float64(cv2.boxPoints(rect))

    # be youhuad
    def extract_triangle_features(self, contour):
        """提取三角形特征 - 返回三个有序角点和平均边长"""
        # 1. 轮廓有效性验证
        if contour is None or len(contour) < 3:
            return None, None

        # === 关键修复：强制转换轮廓数据类型 ===
        try:
            # 转换为OpenCV要求的32位浮点型/整型
            if contour.dtype != np.float32 and contour.dtype != np.int32:
                contour = contour.astype(np.float32)
        except:
            return None, None

        # 2. 计算凸包（增加异常捕获）
        try:
            hull = cv2.convexHull(contour)  # 修复后此处不再报错
        except Exception as e:
            print(f"凸包计算异常: {str(e)}")
            return None, None

        if len(hull) < 3:
            return None, None

        # 方法1：凸包点数正好为3
        if len(hull) == 3:
            points = hull.reshape(3, 2)
        else:
            # 方法2：寻找面积最大的三角形顶点
            max_area = 0
            best_points = None

            # 遍历所有三点组合
            for i in range(len(hull)):
                for j in range(i + 1, len(hull)):
                    for k in range(j + 1, len(hull)):
                        pts = np.array([hull[i][0], hull[j][0], hull[k][0]])
                        area = cv2.contourArea(pts)

                        if area > max_area:
                            max_area = area
                            best_points = pts

            if best_points is None:
                return None, None
            points = best_points

        # 角点排序（顺时针：左上→右上→右下）
        def sort_triangle_vertices(pts):
            # 按y坐标排序
            y_sorted = pts[np.argsort(pts[:, 1])]
            # 取y值最小的两个点（顶部点）
            top_points = y_sorted[:2]
            # 顶部点按x坐标排序
            top_points = top_points[np.argsort(top_points[:, 0])]
            tl, tr = top_points  # 左上，右上
            br = y_sorted[2]  # 右下
            return np.array([tl, tr, br])

        sorted_points = sort_triangle_vertices(points)

        # 计算边长
        side_lengths = [
            np.linalg.norm(sorted_points[0] - sorted_points[1]),  # 上边
            np.linalg.norm(sorted_points[1] - sorted_points[2]),  # 右边
            np.linalg.norm(sorted_points[2] - sorted_points[0]),  # 左边
        ]

        # 计算平均边长
        avg_side = np.mean(side_lengths)

        return sorted_points, avg_side

    # def extract_triangle_features(self, contour):
    #     """高精度提取三角形特征 - 亚像素级优化+几何拟合
    #     Args:
    #         contour: 输入轮廓 (N,1,2)
    #     Returns:
    #         sorted_points: 优化后的三个角点 [左上, 右上, 右下]
    #         avg_side: 亚像素级平均边长
    #     """
    #     # ===== 1. 轮廓预处理 =====
    #     if contour is None or len(contour) < 3:
    #         return None, None
    #
    #     # 转换为浮点型并移除重复点
    #     contour = contour.astype(np.float32).reshape(-1, 2)
    #     contour = np.unique(contour, axis=0)  # 移除重复点
    #
    #     # 计算凸包保证凸性
    #     try:
    #         hull = cv2.convexHull(contour.reshape(-1, 1, 2)).reshape(-1, 2)
    #         if len(hull) < 3:
    #             return None, None
    #     except Exception as e:
    #         print(f"凸包计算异常: {str(e)}")
    #         return None, None
    #
    #     # ===== 2. 顶点优化 =====
    #     # 方法1：多边形逼近优先
    #     epsilon = 0.015 * cv2.arcLength(contour, True)  # 更严格的逼近系数
    #     approx = cv2.approxPolyDP(contour.reshape(-1, 1, 2), epsilon, True).reshape(
    #         -1, 2
    #     )
    #
    #     if len(approx) == 3:
    #         points = approx
    #     else:
    #         # 方法2：最小外接三角形
    #         try:
    #             _, triangle_pts = cv2.minEnclosingTriangle(contour)
    #             points = triangle_pts.reshape(3, 2)
    #         except:
    #             # 回退到凸包顶点
    #             if len(hull) == 3:
    #                 points = hull
    #             else:
    #                 # 选择凸包上面积最大的三点[7](@ref)
    #                 max_area = 0
    #                 best_points = None
    #                 for i in range(len(hull)):
    #                     for j in range(i + 1, len(hull)):
    #                         for k in range(j + 1, len(hull)):
    #                             pts = np.array([hull[i], hull[j], hull[k]])
    #                             area = cv2.contourArea(pts.reshape(-1, 1, 2))
    #                             if area > max_area:
    #                                 max_area = area
    #                                 best_points = pts
    #                 points = best_points if best_points is not None else hull[:3]
    #
    #     # ===== 3. 亚像素级顶点优化 =====
    #     def optimize_vertex(pts, window_size=5):  # 减小窗口尺寸[1](@ref)
    #         """亚像素级角点优化"""
    #         optimized = []
    #         margin = window_size * 2 + 5  # 动态安全边界
    #
    #         for pt in pts:
    #             x, y = pt[0], pt[1]  # 保持浮点精度
    #
    #             # 检查是否在安全边界内
    #             if (
    #                 hasattr(self, "gray_image")
    #                 and self.gray_image is not None
    #                 and margin < x < self.gray_image.shape[1] - margin
    #                 and margin < y < self.gray_image.shape[0] - margin
    #             ):
    #
    #                 # 创建搜索窗口
    #                 x1 = max(0, int(x) - window_size)
    #                 y1 = max(0, int(y) - window_size)
    #                 x2 = min(self.gray_image.shape[1], int(
    #                     x) + window_size + 1)
    #                 y2 = min(self.gray_image.shape[0], int(
    #                     y) + window_size + 1)
    #
    #                 # 提取窗口内轮廓点
    #                 window_contour = []
    #                 for p in contour:
    #                     if x1 <= p[0] <= x2 and y1 <= p[1] <= y2:
    #                         window_contour.append(p)
    #
    #                 if len(window_contour) > 5:
    #                     # 最小二乘拟合直线
    #                     X = np.array(window_contour)
    #                     centroid = np.mean(X, axis=0)
    #                     cov = (X - centroid).T @ (X - centroid)
    #                     _, _, Vt = np.linalg.svd(cov)
    #                     normal = Vt[0]  # 主成分方向
    #
    #                     # 求直线参数 (ax+by+c=0)
    #                     a, b = normal
    #                     c = -np.dot(normal, centroid)
    #                     optimized.append((a, b, c))
    #                 else:
    #                     optimized.append(None)
    #             else:
    #                 optimized.append(None)  # 边界点不优化
    #
    #         # 解直线交点
    #         if all(o is not None for o in optimized):
    #             final_points = []
    #             for i in range(3):
    #                 a1, b1, c1 = optimized[i]
    #                 a2, b2, c2 = optimized[(i + 1) % 3]
    #                 A = np.array([[a1, b1], [a2, b2]])
    #                 b = np.array([-c1, -c2])
    #                 try:
    #                     pt = np.linalg.solve(A, b)
    #                     final_points.append(pt)
    #                 except:
    #                     final_points.append(points[i])
    #             return np.array(final_points)
    #         return points
    #
    #     # 仅在类中存储灰度图时启用
    #     if hasattr(self, "gray_image") and self.gray_image is not None:
    #         points = optimize_vertex(points)
    #
    #     # ===== 4. 顶点排序 =====
    #     def sort_triangle_vertices(pts):
    #         """几何稳定的顶点排序"""
    #         # 计算质心
    #         centroid = np.mean(pts, axis=0)
    #
    #         # 计算相对向量的极角
    #         vectors = pts - centroid
    #         angles = np.arctan2(vectors[:, 1], vectors[:, 0])  # 注意图像坐标系Y轴向下
    #
    #         # 按顺时针排序 (左上→右上→右下)
    #         sorted_idx = np.argsort(angles)[::-1]  # 从大到小排序实现顺时针
    #
    #         # 调整顺序确保第一个点是y最小的
    #         y_sorted_idx = np.argsort(pts[sorted_idx][:, 1])
    #         return pts[sorted_idx][y_sorted_idx]
    #
    #     sorted_points = sort_triangle_vertices(points)
    #
    #     # ===== 5. 高精度边长计算 =====
    #     def precise_distance(p1, p2):
    #         """双精度距离计算"""
    #         dx = p2[0] - p1[0]
    #         dy = p2[1] - p1[1]
    #         return np.sqrt(dx * dx + dy * dy)  # 避免np.linalg.norm的精度损失
    #
    #     side_lengths = [
    #         precise_distance(sorted_points[0], sorted_points[1]),
    #         precise_distance(sorted_points[1], sorted_points[2]),
    #         precise_distance(sorted_points[2], sorted_points[0]),
    #     ]
    #
    #     # 加权平均（考虑角度权重）
    #     angles = [
    #         np.arccos(
    #             np.clip(
    #                 np.dot(
    #                     (sorted_points[1] - sorted_points[0]) /
    #                     side_lengths[0],
    #                     (sorted_points[2] - sorted_points[0]) /
    #                     side_lengths[2],
    #                 ),
    #                 -1,
    #                 1,
    #             )
    #         ),
    #         np.arccos(
    #             np.clip(
    #                 np.dot(
    #                     (sorted_points[0] - sorted_points[1]) /
    #                     side_lengths[0],
    #                     (sorted_points[2] - sorted_points[1]) /
    #                     side_lengths[1],
    #                 ),
    #                 -1,
    #                 1,
    #             )
    #         ),
    #         np.arccos(
    #             np.clip(
    #                 np.dot(
    #                     (sorted_points[0] - sorted_points[2]) /
    #                     side_lengths[2],
    #                     (sorted_points[1] - sorted_points[2]) /
    #                     side_lengths[1],
    #                 ),
    #                 -1,
    #                 1,
    #             )
    #         ),
    #     ]
    #
    #     # 角度加权平均
    #     total_angle = sum(angles)
    #     weights = [angle / total_angle for angle in angles]
    #     avg_side = sum(w * l for w, l in zip(weights, side_lengths))
    #
    #     return sorted_points, avg_side

    # def extract_triangle_features(self, contour):
    #     """提取三角形特征 - 使用面积最大法优化顶点提取"""
    #     # 计算轮廓的凸包
    #     hull = cv2.convexHull(contour)
    #
    #     # 确保有足够的点形成三角形
    #     if len(hull) < 3:
    #         return None
    #
    #     # 方法1：如果凸包点数正好为3，直接返回顶点
    #     if len(hull) == 3:
    #         return hull.reshape(3, 2)
    #
    #     # 方法2：使用面积最大的三角形顶点
    #     max_area = 0
    #     best_points = None
    #
    #     # 计算所有三点组合形成的三角形面积
    #     for i in range(len(hull)):
    #         for j in range(i + 1, len(hull)):
    #             for k in range(j + 1, len(hull)):
    #                 # 获取三个点
    #                 pts = np.array([hull[i][0], hull[j][0], hull[k][0]])
    #
    #                 # 计算三角形面积
    #                 area = cv2.contourArea(pts)
    #
    #                 # 记录最大面积的三角形
    #                 if area > max_area:
    #                     max_area = area
    #                     best_points = pts
    #
    #     return best_points

    # be youhuad
    # def extract_circle_features(self, contour):
    #     """提取圆形特征 - 返回圆心坐标和直径"""
    #     # 1. 验证轮廓有效性
    #     if contour is None or len(contour) < 3:
    #         print("轮廓无效：空或点数不足")
    #         return None, None
    #
    #     # 2. 强制转换数据类型
    #     try:
    #         if contour.dtype not in (np.float32, np.int32):
    #             contour = contour.astype(np.float32)  # 转为OpenCV要求的32位浮点
    #     except Exception as e:
    #         print(f"数据类型转换失败：{str(e)}")
    #         return None, None
    #
    #     # 3. 执行计算（含异常捕获）
    #     try:
    #         (x, y), radius = cv2.minEnclosingCircle(contour)
    #         return np.array([x, y], dtype=np.float32), float(radius * 2)
    #     except cv2.error as e:
    #         print(f"OpenCV错误：{str(e)}")
    #         return None, None
    #     except Exception as e:
    #         print(f"未知错误：{str(e)}")
    #         return None, None
    def extract_circle_features(self, contour):
        """高精度提取圆形特征 - 亚像素级优化+椭圆拟合
        Args:
            contour: 输入轮廓 (N,1,2)
        Returns:
            center: 优化后的圆心坐标 [x, y]
            diameter: 亚像素级直径
        """
        # ===== 1. 轮廓预处理 =====
        if contour is None or len(contour) < 15:  # 至少需要15个点保证拟合精度
            return None, None

        # 转换为浮点型并移除重复点
        contour = contour.astype(np.float32).reshape(-1, 2)
        contour = np.unique(contour, axis=0)

        # ===== 2. 亚像素级轮廓优化 =====
        if hasattr(self, "gray_image") and self.gray_image is not None:
            # 在类中存储灰度图时可启用亚像素优化
            refined_contour = []
            win_size = 5  # 减小窗口尺寸避免边界问题[1](@ref)
            margin = win_size * 2 + 5  # 动态计算安全边界

            for pt in contour:
                x, y = pt[0], pt[1]  # 保持浮点精度[1](@ref)

                # 动态边界检查[1](@ref)
                if (
                    margin < x < self.gray_image.shape[1] - margin
                    and margin < y < self.gray_image.shape[0] - margin
                ):

                    # 5x5窗口亚像素优化[3](@ref)
                    win = (win_size, win_size)
                    zero_zone = (-1, -1)
                    criteria = (
                        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                        30,
                        0.001,
                    )
                    pt_refined = np.array([[x, y]], dtype=np.float32)

                    try:
                        cv2.cornerSubPix(
                            self.gray_image, pt_refined, win, zero_zone, criteria
                        )
                        refined_contour.append(pt_refined[0])
                    except cv2.error as e:
                        # 安全捕获OpenCV错误
                        refined_contour.append(pt)
                else:
                    refined_contour.append(pt)  # 边界点使用原始坐标
            contour = np.array(refined_contour)

        # ===== 3. 椭圆拟合替代最小外接圆 =====
        try:
            # 椭圆拟合（需至少5个点）
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (center, axes, _) = ellipse

                # 椭圆→正圆转换（取长短轴平均值）
                diameter = (axes[0] + axes[1]) / 2
            else:
                # 点不足时回退到最小外接圆
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center, diameter = (x, y), radius * 2
        except cv2.error:
            return None, None

        # ===== 4. 几何约束验证 =====
        # 计算轮廓面积与拟合圆面积比值
        contour_area = cv2.contourArea(contour)
        circle_area = np.pi * (diameter / 2) ** 2

        # 圆形度验证（0.85-1.15为合理范围）
        if not 0.85 <= contour_area / circle_area <= 1.15:
            return None, None  # 非圆形轮廓

        # ===== 5. 高精度直径计算 =====
        # 基于轮廓点到圆心距离加权平均
        distances = []
        weights = []

        for pt in contour:
            dx = pt[0] - center[0]
            dy = pt[1] - center[1]
            dist = np.sqrt(dx * dx + dy * dy)

            # 梯度权重：边缘梯度越大权重越高
            if hasattr(self, "gray_image") and self.gray_image is not None:
                try:
                    # 安全获取梯度信息
                    gx = cv2.Scharr(self.gray_image,
                                    cv2.CV_32F, 1, 0, scale=0.5)
                    gy = cv2.Scharr(self.gray_image,
                                    cv2.CV_32F, 0, 1, scale=0.5)
                    grad_mag = np.sqrt(
                        gx[int(pt[1]), int(pt[0])] ** 2
                        + gy[int(pt[1]), int(pt[0])] ** 2
                    )
                    weights.append(grad_mag)
                except:
                    weights.append(1.0)
            else:
                weights.append(1.0)

            distances.append(dist)

        # 加权平均直径
        avg_radius = np.average(distances, weights=weights)
        final_diameter = 2 * avg_radius

        return np.array(center, dtype=np.float32), final_diameter

    def extract_ellipse_features(self, contour):
        """提取椭圆特征 - 长轴和短轴的四个端点"""
        try:
            ellipse = cv2.fitEllipse(contour)
            center, axes, angle = ellipse
            angle_rad = np.deg2rad(angle)
            direction_x = np.array([np.cos(angle_rad), np.sin(angle_rad)])
            direction_y = np.array([-np.sin(angle_rad), np.cos(angle_rad)])
            half_major = axes[0] / 2
            half_minor = axes[1] / 2
            center = np.array(center)
            pt1 = center + half_major * direction_x
            pt2 = center - half_major * direction_x
            pt3 = center + half_minor * direction_y
            pt4 = center - half_minor * direction_y
            return np.float64([pt1, pt2, pt3, pt4])
        except:
            return None

    def calculate_rectangle_on_board_features(self, features):
        """计算长方形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        edges = [
            (features[1] - features[0]),
            (features[0] - features[1]),
            (features[2] - features[1]),
            (features[1] - features[2]),
        ]
        vector_lengths = [np.linalg.norm(v) for v in edges]
        max_length = max(vector_lengths)
        long_vectors = [
            v for i, v in enumerate(edges) if vector_lengths[i] > 0.9 * max_length
        ]
        long_vectors = [v / np.linalg.norm(v) for v in long_vectors]

        best_angle = None
        min_angle = float("inf")
        for vec in long_vectors:
            angle = self._calculate_vector_angle(
                vec, self.reference_short_edge)
            if abs(angle) < abs(min_angle):
                min_angle = angle
                best_angle = angle

        return center, best_angle

    def calculate_board_on_board_features(self, features):
        """计算板子特征：中心点"""
        center = np.mean(features, axis=0)
        edges = [
            (features[1] - features[0]),
            (features[0] - features[1]),
            (features[2] - features[1]),
            (features[1] - features[2]),
        ]
        vector_lengths = [np.linalg.norm(v) for v in edges]
        max_length = max(vector_lengths)
        long_vectors = [
            v for i, v in enumerate(edges) if vector_lengths[i] > 0.9 * max_length
        ]
        long_vectors = [v / np.linalg.norm(v) for v in long_vectors]

        centers_on_board = self._centers_on_board(features)

        return center, 0, centers_on_board

    def calculate_square_on_board_features(self, features):
        """计算方形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        possible_vectors = []
        for i in range(4):
            next_idx = (i + 1) % 4
            possible_vectors.append(features[next_idx] - features[i])
            possible_vectors.append(features[i] - features[next_idx])

        valid_vectors = [v for v in possible_vectors if np.linalg.norm(v) > 0]
        valid_vectors = [v / np.linalg.norm(v) for v in valid_vectors]

        best_angle = None
        min_angle = float("inf")
        for vec in valid_vectors:
            angle = self._calculate_vector_angle(
                vec, self.reference_short_edge)
            if abs(angle) < abs(min_angle):
                min_angle = angle
                best_angle = angle

        return center, best_angle

    def calculate_triangle_on_board_features(self, features):
        """计算三角形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        left_point_index = None
        min_left = float("inf")
        for i, point in enumerate(features):
            if point[0] < min_left:
                min_left = point[0]
                left_point_index = i
        features = np.delete(features, left_point_index)
        best_point = None
        best_vec = None
        min_angle = float("inf")
        for point in features:
            current_vec = center - point
            current_angle = self._calculate_vector_angle(
                current_vec, self.reference_short_edge
            )
            if abs(current_angle) < abs(min_angle):
                min_angle = current_angle
                best_point = point
                best_vec = current_vec

        return center, min_angle

    def calculate_circle_on_board_features(self, features):
        """计算圆形特征：圆心"""
        return features, 0

    def calculate_ellipse_on_board_features(self, features):
        """计算椭圆特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        major_axis = features[2] - features[3]
        major_axis_norm = major_axis / np.linalg.norm(major_axis)
        angle = self._calculate_vector_angle(
            major_axis_norm, self.reference_short_edge)
        return center, angle

    # no on board features

    def calculate_rectangle_features(self, features):
        """计算长方形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        edges = [
            (features[1] - features[0]),
            (features[0] - features[1]),
            (features[2] - features[1]),
            (features[1] - features[2]),
        ]
        vector_lengths = [np.linalg.norm(v) for v in edges]
        max_length = max(vector_lengths)
        long_vectors = [
            v for i, v in enumerate(edges) if vector_lengths[i] > 0.9 * max_length
        ]
        long_vectors = [v / np.linalg.norm(v) for v in long_vectors]

        best_angle = None
        min_angle = float("inf")
        for vec in long_vectors:
            angle = self._calculate_vector_angle(
                vec, self.reference_short_edge)
            if abs(angle) < abs(min_angle):
                min_angle = angle
                best_angle = angle

        return center, best_angle

    def calculate_board_features(self, features):
        """计算板子特征：中心点"""
        center = np.mean(features, axis=0)
        edges = [
            (features[1] - features[0]),
            (features[0] - features[1]),
            (features[2] - features[1]),
            (features[1] - features[2]),
        ]
        vector_lengths = [np.linalg.norm(v) for v in edges]
        max_length = max(vector_lengths)
        long_vectors = [
            v for i, v in enumerate(edges) if vector_lengths[i] > 0.9 * max_length
        ]
        long_vectors = [v / np.linalg.norm(v) for v in long_vectors]

        centers_on_board = self._centers_on_board(features)

        return center, 0, centers_on_board

    def calculate_square_features(self, features):
        """计算方形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        possible_vectors = []
        for i in range(4):
            next_idx = (i + 1) % 4
            possible_vectors.append(features[next_idx] - features[i])
            possible_vectors.append(features[i] - features[next_idx])

        valid_vectors = [v for v in possible_vectors if np.linalg.norm(v) > 0]
        valid_vectors = [v / np.linalg.norm(v) for v in valid_vectors]

        best_angle = None
        min_angle = float("inf")
        for vec in valid_vectors:
            angle = self._calculate_vector_angle(
                vec, self.reference_short_edge)
            if abs(angle) < abs(min_angle):
                min_angle = angle
                best_angle = angle

        return center, best_angle

    def calculate_triangle_features(self, features):
        """计算三角形特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        left_point_index = None
        min_left = float("inf")
        for i, point in enumerate(features):
            if point[0] < min_left:
                min_left = point[0]
                left_point_index = i
        features = np.delete(features, left_point_index)
        best_point = None
        best_vec = None
        min_angle = float("inf")
        for point in features:
            current_vec = center - point
            current_angle = self._calculate_vector_angle(
                current_vec, self.reference_short_edge
            )
            if abs(current_angle) < abs(min_angle):
                min_angle = current_angle
                best_point = point
                best_vec = current_vec

        return center, min_angle

    def calculate_rectangle_features_plus(self, features_in, features_to):
        """
        计算长方形特征：旋转中心和旋转角度（使当前长方形姿态匹配目标长方形）

        参数:
            features_in: 当前长方形顶点 (4x2数组)
            features_to: 目标姿态长方形顶点 (4x2数组)

        返回:
            center: 旋转中心（当前长方形的中心点）
            rotation_angle: 需要旋转的角度（度）
        """
        # 1. 计算两个长方形的中心点
        center_in = np.mean(features_in, axis=0)
        center_to = np.mean(features_to, axis=0)

        # 2. 计算长方形主要方向向量（最长边方向）
        def compute_longest_edge_vector(points):
            # 计算所有可能的边
            edges = []
            for i in range(4):
                next_idx = (i + 1) % 4
                edge_vector = points[next_idx] - points[i]
                edges.append(edge_vector)

            # 找出最长的边
            edge_lengths = [np.linalg.norm(vec) for vec in edges]
            longest_idx = np.argmax(edge_lengths)

            # 返回归一化后的最长边方向向量
            longest_edge = edges[longest_idx]
            return longest_edge / edge_lengths[longest_idx]

        # 3. 计算两个长方形的方向向量
        dir_in = compute_longest_edge_vector(features_in)
        dir_to = compute_longest_edge_vector(features_to)

        # 4. 计算两个方向向量之间的角度差
        dot_product = np.dot(dir_in, dir_to)
        cross_product = np.cross(dir_in, dir_to)
        angle_rad = np.arctan2(cross_product, dot_product)
        rotation_angle = np.degrees(angle_rad)

        # 5. 角度归一化到 [-180, 180]
        if rotation_angle > 180:
            rotation_angle -= 360
        elif rotation_angle < -180:
            rotation_angle += 360

        return center_in, rotation_angle

    def calculate_square_features_plus(self, features_in, features_to):
        """
        计算方形特征：旋转中心和旋转角度（使当前方形姿态匹配目标方形）

        参数:
            features_in: 当前方形顶点 (4x2数组)
            features_to: 目标姿态方形顶点 (4x2数组)

        返回:
            center: 旋转中心（当前方形的中心点）
            rotation_angle: 需要旋转的角度（度）
        """
        # 1. 计算两个方形的中心点
        center_in = np.mean(features_in, axis=0)
        center_to = np.mean(features_to, axis=0)

        # 2. 计算方形方向向量（最长边方向）
        def compute_direction_vector(points):
            # 计算所有可能的边向量
            vectors = []
            for i in range(4):
                next_idx = (i + 1) % 4
                vec = points[next_idx] - points[i]
                vectors.append(vec)

            # 找出最长的边作为方向基准
            lengths = [np.linalg.norm(vec) for vec in vectors]
            longest_idx = np.argmax(lengths)

            return vectors[longest_idx] / lengths[longest_idx]

        # 3. 计算两个方形的方向向量
        dir_in = compute_direction_vector(features_in)
        dir_to = compute_direction_vector(features_to)

        # 4. 计算两个方向向量之间的角度差
        dot_product = np.dot(dir_in, dir_to)
        cross_product = np.cross(dir_in, dir_to)
        angle_rad = np.arctan2(cross_product, dot_product)
        rotation_angle = np.degrees(angle_rad)

        # 5. 角度归一化到 [-180, 180]
        if rotation_angle > 180:
            rotation_angle -= 360
        elif rotation_angle < -180:
            rotation_angle += 360

        return center_in, rotation_angle

    def calculate_triangle_features_plus(self, features_in, features_to):
        """
        等边三角形旋转角度计算（遍历所有顶点对应关系，返回最小绝对角度）

        参数:
            features_in: 当前三角形顶点 (3x2数组)
            features_to: 目标姿态三角形顶点 (3x2数组)

        返回:
            min_angle: 最小旋转角度（度）
            best_offset: 最佳顶点偏移索引
        """
        # 1. 计算两个三角形的中心点
        try:
            center_in = np.mean(features_in, axis=0)
        except:
            return None
        try:
            center_to = np.mean(features_to, axis=0)
        except:
            return None

        # 2. 计算旋转向量函数（优化版）
        def compute_direction_vector(points, center):
            # 计算顶点到中心的向量
            vectors = points - center

            # 找出与X轴夹角最小的向量作为基准
            reference_angle = np.inf
            best_vec = None

            for vec in vectors:
                # 计算与X轴的夹角（带方向）
                angle = np.arctan2(vec[1], vec[0])
                abs_angle = abs(angle)

                # 选择角度绝对值最小的向量
                if abs_angle < reference_angle:
                    reference_angle = abs_angle
                    best_vec = vec

            return best_vec / np.linalg.norm(best_vec)

        # 3. 主计算逻辑
        min_angle = float("inf")
        best_offset = 0

        # 遍历所有可能的顶点对应关系 (0°, 120°, 240°旋转)
        for offset in range(3):
            total_angle = 0
            valid_count = 0

            # 计算当前偏移下的角度差
            for i in range(3):
                j = (i + offset) % 3

                # 计算当前向量和目标向量
                vec_in = features_in[i] - center_in
                vec_to = features_to[j] - center_to

                # 归一化向量
                norm_in = np.linalg.norm(vec_in)
                norm_to = np.linalg.norm(vec_to)

                if norm_in > 1e-6 and norm_to > 1e-6:
                    vec_in /= norm_in
                    vec_to /= norm_to

                    # 计算点积和叉积
                    dot = np.dot(vec_in, vec_to)
                    cross = np.cross(vec_in, vec_to)

                    # 计算带符号的角度（度）
                    angle = np.degrees(np.arctan2(cross, dot))
                    total_angle += angle
                    valid_count += 1

            # 计算平均角度
            if valid_count > 0:
                avg_angle = total_angle / valid_count
                abs_angle = abs(avg_angle)

                # 寻找最小绝对角度
                if abs_angle < min_angle:
                    min_angle = abs_angle
                    best_angle = avg_angle
                    best_offset = offset

        return center_in, best_angle

    def calculate_circle_features(self, features):
        """计算圆形特征：圆心"""
        return features, 0.0

    def calculate_ellipse_features(self, features):
        """计算椭圆特征：中心点和旋转角度"""
        center = np.mean(features, axis=0)
        major_axis = features[2] - features[3]
        major_axis_norm = major_axis / np.linalg.norm(major_axis)
        angle = self._calculate_vector_angle(
            major_axis_norm, self.reference_short_edge)
        return center, angle

    def _calculate_vector_angle(self, vector1, vector2):
        """计算两个向量之间的角度（度）"""
        dot_product = np.dot(vector1, vector2)
        cross_product = np.cross(vector1, vector2)
        angle_rad = np.arctan2(cross_product, dot_product)
        angle_deg = np.degrees(angle_rad)
        if angle_deg > 180:
            angle_deg -= 360
        elif angle_deg < -180:
            angle_deg += 360
        return angle_deg

    def set_reference_short_edge(self, boxPoints):
        """设置参考短边"""
        points = boxPoints.reshape(4, 2)
        # edges = [
        #     (points[0] - points[1], np.linalg.norm(points[0] - points[1])),
        #     (points[1] - points[2], np.linalg.norm(points[1] - points[2])),
        #     (points[2] - points[3], np.linalg.norm(points[2] - points[3])),
        #     (points[3] - points[0], np.linalg.norm(points[3] - points[0])),
        # ]
        # shortest_index = np.argmin([edge[1] for edge in edges])
        # short_edge_vector = edges[shortest_index][0]
        # self.reference_short_edge = short_edge_vector / np.linalg.norm(short_edge_vector)
        short_edge_vector, length = points[2] - points[3], np.linalg.norm(
            points[2] - points[3]
        )
        self.reference_short_edge = short_edge_vector / length

    def set_reference_long_edge(self, boxPoints):
        """设置参考长边"""
        points = boxPoints.reshape(4, 2)
        # edges = [
        #     (points[0] - points[1], np.linalg.norm(points[0] - points[1])),
        #     (points[1] - points[2], np.linalg.norm(points[1] - points[2])),
        #     (points[2] - points[3], np.linalg.norm(points[2] - points[3])),
        #     (points[3] - points[0], np.linalg.norm(points[3] - points[0])),
        # ]
        # longest_index = np.argmax([edge[1] for edge in edges])
        # long_edge_vector = edges[longest_index][0]
        long_edge_vector, length = points[0] - points[3], np.linalg.norm(
            points[0] - points[3]
        )
        self.reference_long_edge = np.array(long_edge_vector) / length

    def set_reference_edges(self, board_features):
        """设置参考边（短边和长边）"""
        self.set_reference_short_edge(board_features)
        # print("====================short============")
        # print(self.reference_short_edge)
        self.set_reference_long_edge(board_features)
        # print("=============long==================")
        # print(self.reference_long_edge)

    def _centers_on_board(self, features):
        # boxPoints返回四个点顺序：右下→左下→左上→右上
        board_center = np.mean(features, axis=0)
        # 获取变换后的板中心点
        # transformed_board_center, _ = self.point_transform(board_center, None)
        # print("center_of_board", transformed_board_center)
        # transformed_board_center = np.array(transformed_board_center).flatten()
        # transformed_points = self.features_transform(features)
        # 确保所有数组都是1D向量
        # transformed_points = np.array(transformed_points)
        # transformed_board_center = np.array(transformed_board_center).flatten()
        # 计算局部坐标系基向量
        # try:
        #     # 右下→左下→左上→右上 -> 左上(2), 右上(3), 左下(1)
        #     # pt_ul = features[2]  # 左上
        #     # pt_ur = features[3]  # 右上
        #     # pt_bl = features[1]  # 左下
        #     pt_ul = features[2]  # 左上
        #     pt_ur = features[3]  # 右上
        #     pt_bl = features[1]  # 左下
        #     # X轴方向（从左到右）
        #     vector_x = pt_ur - pt_ul
        #     vector_x /= np.linalg.norm(vector_x)
        #     # Y轴方向（从上到下）
        #     vector_y = pt_bl - pt_ul
        #     vector_y /= np.linalg.norm(vector_y)
        # except Exception as e:
        #     print(f"好正的坐标系啊")
        #     vector_x = np.array([-1.0, 0.0])
        #     vector_y = np.array([0.0, -1.0])
        vector_x = self.reference_long_edge
        vector_y = self.reference_short_edge
        # 计算局部坐标系原点
        # 计算板上各点坐标（在变换后的空间中）
        centers = {}
        # 使用偏移量计算坐标
        # circular (圆)
        offset_x, offset_y = -55 - 0.674, 42 - 11.016
        center_circular = board_center + offset_x * vector_x + offset_y * vector_y
        center_circular[0] = center_circular[0]
        center_circular[1] = center_circular[1]
        centers["circle"] = center_circular
        # square (方形)
        offset_x, offset_y = -(-50 + 1.894 - 2), 40 + 10.925 - 4 + 22.663
        center_square = board_center + offset_x * vector_x + offset_y * vector_y
        center_square[0] = center_square[0]
        center_square[1] = center_square[1]
        centers["square"] = center_square
        # ellipse
        offset_x, offset_y = -68 - 1.508, -36 + 6.411
        center_ellipse = board_center + offset_x * vector_x + offset_y * vector_y
        center_ellipse[0] = center_ellipse[0]
        center_ellipse[1] = center_ellipse[1]
        centers["ellipse"] = center_ellipse
        # rectangle
        offset_x, offset_y = 5 + 4.4 - 12 - 0.5, -37 + 2.267 + 6
        center_rectangle = board_center + offset_x * vector_x + offset_y * vector_y
        center_rectangle[0] = center_rectangle[0]
        center_rectangle[1] = center_rectangle[1]
        centers["rectangle"] = center_rectangle
        # triangle
        offset_x, offset_y = 59 + 2, -39 + 2
        center_triangle = board_center + offset_x * vector_x + offset_y * vector_y
        center_triangle[0] = center_triangle[0]
        center_triangle[1] = center_triangle[1]
        centers["triangle"] = center_triangle

        return centers

    def draw_ordered_corners(self, image, corners):
        """
        在图像上按顺序绘制A4纸的四个角点（左上、右上、右下、左下）

        参数:
            image: 输入图像 (numpy数组)
            corners: 有序的四个角点坐标，格式为：
                    [左上, 右上, 右下, 左下] - 每个点为(x, y)坐标

        返回:
            image: 绘制了角点和连接线的图像
        """
        # 确保有四个角点
        if len(corners) != 4:
            raise ValueError("需要四个角点")

        # 解包角点（按顺序）
        tl, tr, br, bl = corners  # tl=左上, tr=右上, br=右下, bl=左下

        # 1. 绘制角点（不同颜色区分）
        cv2.circle(image, tuple(map(int, tl)), 10, (0, 0, 255), -1)  # 红色: 左上
        cv2.circle(image, tuple(map(int, tr)), 10, (0, 255, 0), -1)  # 绿色: 右上
        cv2.circle(image, tuple(map(int, br)), 10, (255, 0, 0), -1)  # 蓝色: 右下
        cv2.circle(image, tuple(map(int, bl)), 10, (0, 255, 255), -1)  # 黄色: 左下

        # 2. 绘制连接线（显示边界）
        cv2.line(
            image, tuple(map(int, tl)), tuple(map(int, tr)), (255, 0, 255), 2
        )  # 上边
        cv2.line(
            image, tuple(map(int, tr)), tuple(map(int, br)), (255, 0, 255), 2
        )  # 右边
        cv2.line(
            image, tuple(map(int, br)), tuple(map(int, bl)), (255, 0, 255), 2
        )  # 下边
        cv2.line(
            image, tuple(map(int, bl)), tuple(map(int, tl)), (255, 0, 255), 2
        )  # 左边

        # 3. 添加位置标签
        cv2.putText(
            image,
            "TL",
            (int(tl[0]) + 15, int(tl[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )
        cv2.putText(
            image,
            "TR",
            (int(tr[0]) + 15, int(tr[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            image,
            "BR",
            (int(br[0]) + 15, int(br[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2,
        )
        cv2.putText(
            image,
            "BL",
            (int(bl[0]) + 15, int(bl[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )

        return image
