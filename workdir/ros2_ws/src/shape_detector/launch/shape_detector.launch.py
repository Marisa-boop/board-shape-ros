# Copyright (c) 2025 Marisa-boop
# SPDX-License-Identifier: MIT

# from launch import LaunchDescription
# from launch_ros.actions import Node
#
#
# def generate_launch_description():
#     return LaunchDescription(
#         [
#             Node(
#                 package="shape_detector",
#                 executable="shape_detector_node",
#                 name="shape_detector",
#                 output="screen",
#                 parameters=[
#                     {"board_model_path": "./model/board.pt"},
#                     {"shape_model_path": "./model/shape.pt"},
#                     {"number_model_path": "./model/number.pt"},
#                     {"hmin": 131},
#                     {"hmax": 178},
#                     {"smin": 3},
#                     {"smax": 255},
#                     {"vmin": 202},
#                     {"vmax": 255},
#                     {"hmin_no_black": 148},
#                     {"hmax_no_black": 179},
#                     {"smin_no_black": 5},
#                     {"smax_no_black": 34},
#                     {"vmin_no_black": 187},
#                     {"vmax_no_black": 255},
#                 ],
#             )
#         ]
#     )
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 主节点：形状检测器
    shape_detector_node = Node(
        package="shape_detector",
        executable="shape_detector_node",
        name="shape_detector",
        output="screen",
        parameters=[
            {"board_model_path": "./model/board.pt"},
            {"shape_model_path": "./model/shape.pt"},
            {"number_model_path": "./model/number.pt"},
            {"hmin": 131},
            {"hmax": 178},
            {"smin": 3},
            {"smax": 255},
            {"vmin": 202},
            {"vmax": 255},
            {"hmin_no_black": 148},
            {"hmax_no_black": 179},
            {"smin_no_black": 5},
            {"smax_no_black": 34},
            {"vmin_no_black": 187},
            {"vmax_no_black": 255},
        ],
    )

    # MindVision相机节点（通过包含其launch文件）
    mindvision_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [FindPackageShare("mindvision_camera"),
                     "launch", "mv_launch.py"]
                )
            ]
        )
    )

    # RM串口驱动节点（通过包含其launch文件）
    serial_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [
                        FindPackageShare("rm_serial_driver"),
                        "launch",
                        "serial_driver.launch.py",
                    ]
                )
            ]
        )
    )

    return LaunchDescription(
        [
            # 节点启动顺序：先硬件驱动，后处理节点
            mindvision_camera,  # 相机硬件驱动
            serial_driver,  # 串口通信驱动
            shape_detector_node,  # 形状检测处理节点
        ]
    )
