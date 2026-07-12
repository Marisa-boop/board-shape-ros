# Copyright (c) 2025 Marisa-boop
# SPDX-License-Identifier: MIT

import cv2
import numpy as np
import glob


class CameraCalibrator:
    def __init__(self, grid_size=(9, 6), square_size=0.03):
        """
        简化版相机标定器（专注俯仰角和距离校正）
        :param grid_size: 棋盘格内角点数量 (列, 行)
        :param square_size: 棋盘格实际尺寸（单位：米）
        """
        self.grid_size = grid_size
        self.square_size = square_size
        self.calibrated = False
        self.mtx = None  # 相机内参
        self.dist = None  # 畸变系数
        self.pitch_deg = None  # 俯仰角（度）

    def create_object_points(self):
        """创建竖直板子上的棋盘格3D坐标（Y=0平面）"""
        w, h = self.grid_size
        objp = np.zeros((w * h, 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1, 2) * self.square_size
        objp[:, [0, 2]] = objp[:, [2, 0]]  # 交换X和Z轴
        return objp

    def calibrate(self, image_paths):
        """执行标定并计算俯仰角"""
        objp = self.create_object_points()
        objpoints = []  # 3D点
        imgpoints = []  # 2D点
        image_size = None

        for path in image_paths:
            img = cv2.imread(path)
            if image_size is None:
                image_size = (img.shape[1], img.shape[0])

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                gray, self.grid_size, None)

            if ret:
                # 亚像素级角点精确化
                corners = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                )
                objpoints.append(objp)
                imgpoints.append(corners)

        if not objpoints:
            raise ValueError("未检测到有效棋盘格图像")

        # 相机标定
        ret, self.mtx, self.dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None
        )

        if ret:
            self.calibrated = True
            self._calculate_pitch(rvecs[0])
            return True
        return False

    def _calculate_pitch(self, rvec):
        """从旋转向量计算俯仰角（核心算法）"""
        rotation_mat, _ = cv2.Rodrigues(rvec)
        # 关键公式：pitch = arcsin(-R[2,0])
        pitch_rad = np.arcsin(-rotation_mat[2, 0])
        self.pitch_deg = np.degrees(pitch_rad)
        return pitch_rad

    def calculate_board_distance(self, image_points):
        """
        计算相机到竖直板子的校正距离
        :param image_points: 板子上4个角点的图像坐标（顺序：左上，右上，右下，左下）
        :return: 校正后的距离（米）
        """
        if not self.calibrated:
            raise RuntimeError("请先进行相机标定")

        # 创建竖直板子的3D坐标（假设板子尺寸已知）
        board_height = 0.297  # 板子高度（米）
        board_width = 0.210  # 板子宽度（米）
        object_points = np.array(
            [
                [0, 0, 0],  # 左上
                [board_width, 0, 0],  # 右上
                [board_width, 0, -board_height],  # 右下
                [0, 0, -board_height],  # 左下
            ],
            dtype=np.float32,
        )

        # 使用PnP求解位姿
        _, rvec, tvec = cv2.solvePnP(
            object_points, image_points, self.mtx, self.dist)

        # 距离校正（核心公式）
        true_distance = self._apply_pitch_correction(tvec)
        return true_distance

    def _apply_pitch_correction(self, tvec):
        """应用俯仰角校正的两种方法（推荐欧氏距离法）"""
        # 方法1：直接计算欧氏距离（最准确）[3,4](@ref)
        euclidean_distance = np.linalg.norm(tvec)

        # 方法2：俯仰角补偿（当俯仰角已知时）
        if self.pitch_deg is not None:
            pitch_rad = np.radians(self.pitch_deg)
            # 校正公式：实际距离 = tvec_z / cos(pitch)
            corrected_distance = tvec[2][0] / np.cos(pitch_rad)
            return min(euclidean_distance, corrected_distance)  # 返回更可靠的值

        return euclidean_distance


if __name__ == "__main__":
    # 1. 标定相机并获取俯仰角
    calibrator = CameraCalibrator(grid_size=(9, 6), square_size=0.03)
    image_paths = glob.glob("calibration_images/*.jpg")

    if calibrator.calibrate(image_paths):
        print(f"俯仰角: {calibrator.pitch_deg:.2f}°")

        # 2. 测量目标板距离（假设已检测到板子角点）
        # 示例：板子上四个角点的像素坐标（需按左上、右上、右下、左下顺序）
        board_corners = np.array(
            [
                [320, 150],  # 左上
                [480, 160],  # 右上
                [490, 300],  # 右下
                [310, 290],  # 左下
            ],
            dtype=np.float32,
        )

        distance = calibrator.calculate_board_distance(board_corners)
        print(f"相机到竖直板子的距离: {distance:.3f} 米")
