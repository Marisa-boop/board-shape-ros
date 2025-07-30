from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="shape_detector",
                executable="shape_detector_node",
                name="shape_detector",
                output="screen",
                parameters=[
                    {"board_model_path": "./model/board.pt"},
                    {"shape_model_path": "./model/shape.pt"},
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
        ]
    )
