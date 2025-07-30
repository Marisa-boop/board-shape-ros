import yaml
import numpy as np
from typing import List, Tuple


def load_points_from_yaml(file_path: str) -> List[Tuple[int, int]]:
    """
    从YAML文件中加载点坐标

    参数:
        file_path (str): YAML文件路径

    返回:
        List[Tuple[int, int]]: 点坐标列表，格式为[(x1, y1), (x2, y2), ...]
    """
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        # 提取点数据并转换为整数坐标
        points = []
        for point_dict in data["points"]:
            x = int(round(point_dict["x"]))
            y = int(round(point_dict["y"]))
            points.append((x, y))

        return points

    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到")
        return []
    except KeyError as e:
        print(f"错误: YAML文件格式不正确，缺少必需的键: {e}")
        return []
    except Exception as e:
        print(f"加载YAML文件时出错: {e}")
        return []


# ============================== 工具函数 ==============================
def average_corners(corners1, corners2):
    """计算两组角点的几何平均值"""
    assert corners1.shape == (4, 2) and corners2.shape == (4, 2)

    def sort_corners(pts):
        center = np.mean(pts, axis=0)
        angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
        return pts[np.argsort(angles)]

    sorted1 = sort_corners(corners1)
    sorted2 = sort_corners(corners2)
    return (0.5 * sorted1 + 0.5 * sorted2).astype(int)


# 使用示例
if __name__ == "__main__":
    points = load_points_from_yaml("homography_points.yaml")
    print("加载的点坐标:")
    for i, (x, y) in enumerate(points):
        print(f"点{i+1}: ({x}, {y})")
