import cv2
import numpy as np
import yaml

WIN_NAME = "pick_points"
points = []  # 存储点坐标的列表


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
    """

image_width: 1280
image_height: 720
camera_name: camera1
camera_matrix:
  rows: 3
  cols: 3
  data: [661.31951,   0.     , 661.6395 ,
           0.     , 662.05605, 368.61694,
           0.     ,   0.     ,   1.     ]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: 5
  data: [0.004463, -0.008857, -0.000346, -0.001388, 0.000000]
rectification_matrix:
  rows: 3
  cols: 3
  data: [1., 0., 0.,
         0., 1., 0.,
         0., 0., 1.]
projection_matrix:
  rows: 3
  cols: 4
  data: [658.50537,   0.     , 658.9821 ,   0.     ,
           0.     , 661.95245, 367.89184,   0.     ,
           0.     ,   0.     ,   1.     ,   0.     ]
"""
    return cv2.undistort(
        src=frame, cameraMatrix=camera_matrix_data, distCoeffs=dist_coeffs_data
    )


camera_matrix_data = np.array(
    [[661.31951, 0.0, 661.6395], [0.0, 662.05605, 368.61694], [0.0, 0.0, 1.0]],
    dtype=np.float32,
)

dist_coeffs_data = np.array(
    [0.004463, -0.008857, -0.000346, -0.001388, 0.000000], dtype=np.float32
)


def onmouse_pick_points(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"添加点: ({x}, {y})")
        points.append((int(x), int(y)))  # 将点添加到列表


def save_points_to_yaml(file_path):
    # 转换格式: [x1, y1] -> 符合OpenCV的Point2f格式
    points_data = [{"x": float(x), "y": float(y)} for (x, y) in points]

    # 写入YAML文件
    with open(file_path, "w") as f:
        yaml.dump({"points": points_data}, f, default_flow_style=False)
    print(f"保存了 {len(points)} 个点到 {file_path}")


if __name__ == "__main__":
    # 初始化相机
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("错误: 无法访问相机")
        exit()

    # 创建窗口并设置鼠标回调
    cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WIN_NAME, onmouse_pick_points)

    print("操作说明:")
    print(" - 左键点击: 添加点")
    print(" - 按 's': 保存点到YAML文件")
    print(" - 按 'c': 清除所有点")
    print(" - 按 'q': 退出")

    # 主循环
    while True:
        ret, frame = cap.read()
        frame = undistort_image(frame, camera_matrix_data, dist_coeffs_data)
        if not ret:
            print("错误: 无法获取相机帧")
            continue

        # 在实时帧上绘制所有标记点
        display_img = frame.copy()
        for i, pt in enumerate(points):
            cv2.drawMarker(
                display_img,
                pt,
                (0, 255, 0),
                markerType=cv2.MARKER_CROSS,
                markerSize=20,
                thickness=1,
            )
            # 显示点序号
            cv2.putText(
                display_img,
                str(i + 1),
                (pt[0] + 10, pt[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

        # 显示已选择点的数量
        cv2.putText(
            display_img,
            f"Points: {len(points)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow(WIN_NAME, display_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s") and points:  # 保存点
            save_points_to_yaml("./workdir/ros2_ws/config/src_pts.yaml")
        elif key == ord("c"):  # 清除点
            points = []
            print("所有点已清除")
        elif key == ord("q"):  # 退出
            break

    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
