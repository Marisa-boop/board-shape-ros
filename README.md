# Shape Detector — 基于 ROS 2 的视觉检测系统

![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-green) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red) ![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED)

一套完整的计算机视觉流水线，用于检测、测量和分类 A4 纸板上的几何图形。基于 ROS 2 + YOLOv8 + Docker 构建。

**检测流水线：**

摄像头采集 → 板子分割 → 子图提取 → 形状检测 → PnP 测距 → 单应变换 → 特征测量 → 串口输出

---

## 目录

- [系统概述](#系统概述)
- [项目结构](#项目结构)
- [Docker 部署](#docker-部署)
- [ROS 2 系统架构](#ros-2-系统架构)
- [使用的技术](#使用的技术)
- [实现的功能](#实现的功能)
- [模块详解](#模块详解)
- [测试模块](#测试模块)
- [工具脚本](#工具脚本)
- [模型文件](#模型文件)
- [配置文件](#配置文件)

---

## 系统概述

使用摄像头采集视频帧，通过 YOLOv8 分割模型检测带黑色边框的 A4 纸板，然后检测纸板上的几何图形（圆形、正方形、三角形）。利用 PnP 距离估计和单应性坐标变换，测量这些图形的真实世界尺寸（毫米）。结果通过自定义协议（含 CRC16 校验）经串口发送给下位机。当收到串口命令时，还能对正方形上的手写数字进行分类识别。

### 硬件需求

- 摄像头（USB 或 MindVision）— 测试分辨率 1280x720
- NVIDIA GPU（需 CUDA 支持，用于 YOLO 推理）
- 下位机 MCU（如 RoboMaster），用于串口通信
- 带黑色边框的 A4 纸，纸上绘制几何图形

---

## 项目结构

```
detect_shape/
├── docker/
│   ├── Dockerfile              # 多阶段容器构建
│   └── compose.yaml            # Docker Compose 配置
├── scripts/
│   └── run_container.bash      # 一键启动容器
├── config/                     # 相机标定与参数
│   ├── camera_info.yaml
│   ├── params_1.yaml
│   └── params_2.yaml
├── workdir/ros2_ws/
│   ├── model/                  # 训练的 YOLO 模型
│   │   ├── board.pt            # 板子分割模型
│   │   ├── shape.pt            # 形状分割模型
│   │   ├── number.pt           # 数字分类模型
│   │   ├── laser.pt            # 激光检测模型
│   │   └── laser_red.pt
│   ├── config/                 # 单应变换点对
│   │   ├── src_pts.yaml
│   │   └── dst_pts.yaml
│   └── src/
│       ├── shape_detector/     # 主功能包（Python）
│       ├── custom_msgs/        # 自定义消息
│       ├── rm_serial_driver/   # 串口驱动（C++）
│       ├── usb_cam/            # USB 摄像头驱动（C++）
│       └── rm_shared/          # 共享硬件驱动
├── test/
│   └── test_number.py          # 数字分类器测试
├── test_pipeline.py            # 完整流水线测试
├── utils/                      # 工具脚本
│   ├── calibration_pts.py      # 标定点选取
│   ├── gen_pic_base.py         # A4 模板生成
│   ├── gen_pic_circle.py       # 圆形测试图生成
│   ├── gen_pic_square.py       # 正方形测试图生成
│   ├── gen_pic_triangle.py     # 三角形测试图生成
│   ├── save_all.py             # ROS2 视频录制（全图）
│   ├── save_sub.py             # ROS2 视频录制（子图）
│   ├── save_sub_square.py      # ROS2 视频录制（正方形）
│   └── test_h.py               # 单应性测试
├── calib/
│   └── bias.yaml               # PWM 偏置校准
├── notebook/
│   ├── number_test.ipynb
│   └── test.ipynb
└── packages/
    └── requirements.txt        # Python 依赖
```

---

## Docker 部署

### 前置条件

- 安装 Docker 及 NVIDIA Container Toolkit（GPU 加速需要）
- Linux 主机需有 `/dev/video*`（摄像头）和 `/dev/ttyUSB0`（串口）
- X11 服务（如需 GUI 显示，可选）

### 构建与运行

**方式一：使用启动脚本**

```bash
cd detect_shape
bash scripts/run_container.bash
```

**方式二：使用 docker compose**

```bash
cd detect_shape/docker
docker compose up --build
```

**方式三：手动运行**

```bash
cd detect_shape
docker build -f docker/Dockerfile -t shape_detector .
docker run --rm -it \
  --gpus all \
  --network host \
  --privileged \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /dev/dri:/dev/dri \
  -v /dev/video0:/dev/video2 \
  -v $(pwd)/workdir:/ros2_ws \
  shape_detector
```

### 容器说明

Dockerfile 使用**多阶段构建**：

| 阶段 | 基础镜像 | 作用 |
|------|---------|------|
| `base` | `nvcr.io/nvidia/pytorch:24.04-py3` | 系统依赖 + Python 包 |
| `ros2` | `base` | ROS 2 Jazzy + 编译工具 |
| `final` | `ros2` | 编译 ROS 2 工作空间，启动 launch 文件 |

关键特性：
- Ubuntu 24.04 (Noble) + NVIDIA PyTorch 基础镜像
- ROS 2 Jazzy + ultralytics（YOLOv8）
- GPU 加速（NVIDIA Container Toolkit）
- 网络模式 `host`（ROS 2 DDS 发现需要）
- 特权模式（访问 USB/摄像头设备）

**docker-compose.yaml** 挂载：
- `./workdir` → `/ros2_ws`（ROS 2 工作空间，含模型和源码）
- `/dev/video*` 摄像头设备
- `/tmp/.X11-unix` GUI 显示

---

## ROS 2 系统架构

### shape_detector 包

**语言：** Python
**入口点：** `shape_detector_node`
**依赖：** `rclpy`, `sensor_msgs`, `cv_bridge`, `std_msgs`, `geometry_msgs`, `custom_msgs`

主 ROS 2 节点，编排整个视觉流水线。接收摄像头图像，运行检测流水线，发布结果。

**订阅话题：**
- `/image_raw`（`sensor_msgs/Image`）— 摄像头输入
- `/received_data`（`custom_msgs/ReceivedData`）— 下位机串口数据（触发数字分类模式）

**发布话题：**
- `result_image`（`sensor_msgs/Image`）— 带标注的全帧图像
- `result_sub_image`（`sensor_msgs/Image`）— 带形状标注的子图
- `result_sub_origin_image`（`sensor_msgs/Image`）— 原始子图（板子裁剪）
- `sub_square_image`（`sensor_msgs/Image`）— 提取的正方形子图（用于数字分类）
- `number_image`（`sensor_msgs/Image`）— 数字分类可视化
- `detect_result`（`custom_msgs/DetectResult`）— 检测结果（供串口发送）

**参数（在 launch 文件中声明）：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `board_model_path` | `./model/board.pt` | 板子分割模型路径 |
| `shape_model_path` | `./model/shape.pt` | 形状分割模型路径 |
| `number_model_path` | `./model/number.pt` | 数字分类模型路径 |
| `hmin/hmax/smin/smax/vmin/vmax` | HSV 范围 | 颜色滤波参数 |
| `hmin_no_black/...` | HSV 范围 | 黑底上的颜色滤波参数 |

### custom_msgs 包

两种自定义消息类型：

**`DetectResult.msg`：**
```
std_msgs/Header header
float32 depth           # 相机到板子距离（mm）
float32 length          # 形状尺寸（mm）：半径/直径/边长
float32 is_received     # 数字分类标志（0 或 1）
```

**`ReceivedData.msg`：**
```
std_msgs/Header header
uint8 number            # 从下位机收到的目标数字
```

### rm_serial_driver 包

**语言：** C++
**作用：** 视觉计算机与下位机之间的串口通信。

**串口配置：** `/dev/ttyUSB0`，115200 波特率，8N1

**数据包协议：**

接收包（下位机 → 计算机）：
```
[0xFF] [number] [0xFA]
```

发送包（计算机 → 下位机）：
```
[0xFF] [depth: float32] [length: float32] [is_received: float32] [0xFA] [checksum: uint16]
```

- 发送包使用 CRC16 校验（多项式 0x1021）
- 节点订阅 `/detect_result`，发布 `/received_data`

### usb_cam 包

**语言：** C++
标准 ROS 2 USB 摄像头驱动，两种参数配置：
- `params_1.yaml`：1280x720，MJPEG，30 FPS
- `params_2.yaml`：640x480，MJPEG，15 FPS

### 话题数据流

```
                    ┌──────────────────┐
                    │   摄像头驱动       │
                    │  (usb_cam /       │
                    │   mindvision)     │
                    └────────┬─────────┘
                             │ /image_raw
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │  ShapeDetector   │
                    │     Node         │
                    │                  │
                    └──┬───┬───┬───┬──┘
                       │   │   │   │
         ┌─────────────┘   │   │   └──────────────┐
         ▼                 ▼   ▼                  ▼
   ┌──────────┐   ┌──────────────┐        ┌──────────────┐
   │detect_   │   │ result_image │  ...   │ number_image │
   │result    │   │ /sub/...     │        │              │
   └────┬─────┘   └──────────────┘        └──────────────┘
        │
        ▼
   ┌──────────┐        ┌──────────────┐
   │RM Serial │◄──────►│   下位机 MCU  │
   │  Driver  │        │              │
   └──────────┘        └──────────────┘
        │
        ▼
   /received_data
        │
        ▼
   ShapeDetector Node（触发数字模式）
```

### Launch 文件

`shape_detector.launch.py` 按顺序启动三个组件：

```python
def generate_launch_description():
    shape_detector_node = Node(
        package="shape_detector",
        executable="shape_detector_node",
        name="shape_detector",
        output="screen",
        parameters=[
            {"board_model_path": "./model/board.pt"},
            {"shape_model_path": "./model/shape.pt"},
            {"number_model_path": "./model/number.pt"},
            # ... HSV 参数
        ],
    )

    mindvision_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("mindvision_camera"),
                "launch", "mv_launch.py"
            ])
        ])
    )

    serial_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("rm_serial_driver"),
                "launch", "serial_driver.launch.py"
            ])
        ])
    )

    return LaunchDescription([
        mindvision_camera,    # 相机硬件驱动
        serial_driver,        # 串口通信驱动
        shape_detector_node,  # 形状检测处理节点
    ])
```

---

## 使用的技术

| 技术 | 用途 |
|------|------|
| **ROS 2** (Jazzy) | 机器人中间件与节点编排 |
| **YOLOv8** (Ultralytics) | 目标检测、分割与分类 |
| **OpenCV** | 图像处理、相机标定、特征提取 |
| **PyTorch** | 深度学习框架 |
| **CUDA** | GPU 加速 |
| **Docker** | 容器化部署 |
| **colcon** | ROS 2 编译系统 |
| **cv_bridge** | ROS ↔ OpenCV 图像转换 |
| **Eigen3** | 线性代数库（C++） |

---

## 实现的功能

### 1. A4 板子检测

**文件：** `segmentDetector.py`

使用 YOLOv8 分割模型（`board.pt`）检测带黑色边框的 A4 纸。模型输出板子区域的分割掩码多边形。

```python
from shape_detector.segmentDetector import SegmentDetector

detector = SegmentDetector(model_path="model/board.pt", conf=0.5)
detections = detector.detect(frame)
# 返回列表：[{"xyxy": [...], "conf": 0.95, "cls_id": 0, "cls_name": "board", "polygon": np.ndarray}]
```

### 2. 子图提取

**文件：** `subImageProcesser.py`

使用分割多边形从全帧图像中提取板子区域为 RGBA 子图。Alpha 通道编码掩码，实现干净的背景去除。

```python
processor = SubImageProcessor()
detections = processor.extract_subimages(frame, detections)
subimages = processor.get_subimages()  # 裁剪后的板子图像列表

# 从子图坐标恢复到原图坐标
original_pts = processor.restore_coordinates(detection, subimage_polygon)
```

还提供 `extract_rectangular_subimage()` 用于提取旋转校正后的正方形子图（用于数字分类）：

```python
square_img = processor.extract_rectangular_subimage(subimg, square_polygon)
# 返回 256x256 的仿射变换图像
```

### 3. 形状检测与分类

**文件：** `shapeDetector.py`

YOLOv8 分割模型（`shape.pt`），可检测三类形状：
- `0` → **圆形**（circle）
- `1` → **正方形**（square，支持多实例，带 ID）
- `2` → **三角形**（triangle）

```python
from shape_detector.shapeDetector import ShapeDetector

detector = ShapeDetector(model_path="model/shape.pt")
results = detector.detect(subimg)
# 返回：
# {
#   "circle": {"conf": 0.92, "polygon": np.ndarray, ...} 或 None,
#   "square": [{"conf": 0.95, "polygon": ..., "id": 0}, ...] 或 [],
#   "triangle": {"conf": 0.88, "polygon": ..., ...} 或 None,
# }

# 可视化结果
vis_img = detector.visualize(subimg, results)
```

### 4. 亚像素特征提取

**文件：** `featureProcesser.py`

这是最复杂的模块（1599 行）。使用经典计算机视觉技术从 YOLO 分割多边形中提取精确的几何特征：

**板子角点**（`extract_rectangle_features`）：
- 凸包 → 轮廓逼近 → 通过 `cornerSubPix` 亚像素精化
- 最小外接矩形拟合确保鲁棒初始化

**圆形**（`extract_circle_features`）：
- 亚像素轮廓精化
- 椭圆拟合（`cv2.fitEllipse`）
- 圆形度验证
- 梯度加权直径平均

```python
# 圆形：返回 (中心点, 直径)
pos, diameter = feature_processor.extract_circle_features(circle_polygon)
```

**正方形**（`extract_square_features`）：
- 凸包 → 最小外接矩形初始化
- 通过 `cornerSubPix` 亚像素角点优化
- 每条边的最小二乘直线拟合
- 几何求交得到最终的角点

```python
# 正方形：返回 (4个角点, 边长)
corners, length = feature_processor.extract_square_features(square_polygon)
```

**三角形**（`extract_triangle_features`）：
- 凸包 → 最大面积内接三角形选取

```python
# 三角形：返回 (3个顶点, 边长)
corners, length = feature_processor.extract_triangle_features(triangle_polygon)
```

### 5. PnP 距离测量

**文件：** `pnpSolver.py`

使用 Perspective-n-Point（PnP）算法，根据已知的 A4 尺寸（210×297 mm）估计相机到板子的距离。

```python
from shape_detector.pnpSolver import PnPSolver
import numpy as np

camera_matrix = np.array([
    [1728.27, 0.0, 569.30],
    [0.0, 1729.86, 418.91],
    [0.0, 0.0, 1.0]
], dtype=np.float32)
dist_coeffs = np.array([-0.080, 0.469, -0.013, -0.003, 0.0], dtype=np.float32)

solver = PnPSolver(camera_matrix, dist_coeffs, method=cv2.SOLVEPNP_EPNP)

object_points = np.array([
    [0.0, 0.0, 0.0],      # 左上
    [210.0, 0.0, 0.0],    # 右上
    [210.0, 297.0, 0.0],  # 右下
    [0.0, 297.0, 0.0]     # 左下
], dtype=np.float32)

success, rvec, tvec = solver.solve(object_points, image_corners)
distance = tvec[2][0]  # Z 方向距离，单位 mm
```

### 6. 单应变换

**文件：** `transformer.py`

计算从像素坐标到真实世界 A4 纸坐标（毫米）的透视变换。每帧使用实际检测到的板子角点更新单应矩阵，提高鲁棒性。

```python
from shape_detector.transformer import HomographyTransformer

# 用参考点对初始化
transformer = HomographyTransformer(src_points=src_pts, dst_points=dst_pts)

# 用实际板子角点更新（每帧调用）
transformer.update_src_points(board_corners)
transformer.recompute_homography()

# 从像素坐标变换到真实世界坐标
real_pt = transformer.transform_point(pixel_pt)

# 变换多个点
real_polygon = transformer.transform_features(pixel_polygon)

# 整图透视变换
warped = transformer.warp_frame(frame)
```

**配置文件：**

`config/src_pts.yaml` — A4 纸角点的 4 个像素坐标：
```yaml
points:
  - [96, 62]
  - [509, 101]
  - [504, 403]
  - [59, 389]
```

`config/dst_pts.yaml` — 对应的真实世界坐标（mm）：
```yaml
points:
  - [0, 0]       # 左上
  - [210, 0]     # 右上
  - [210, 297]   # 右下
  - [0, 297]     # 左下
```

### 7. 数字分类

**文件：** `numberClassify.py`

YOLOv8 分类模型（`number.pt`），用于识别正方形上的数字 0–9。由下位机的串口命令触发。进入"数字分类模式"后，系统提取每个检测到的正方形，运行分类器，选择对目标数字置信度最高的正方形。

```python
from shape_detector.numberClassify import NumberClassifier

classifier = NumberClassifier(model_path="model/number.pt")

# 获取特定数字的置信度
confidence = classifier.detect(square_image, set_number=5)
# 返回 float 置信度，低于阈值返回 None

# 或获取 top-1 预测
result = classifier.detect(square_image)
# 返回 (digit, confidence) 元组或 None

# 可视化
vis = classifier.visualize(image, predicted_number)
```

### 8. 串口通信

**文件：** `rm_serial_driver`（C++）

与下位机双向串口通信，使用自定义二进制数据包协议 + CRC16 校验：

- **接收**（下位机 → 计算机）：目标数字，触发数字分类模式
- **发送**（计算机 → 下位机）：检测结果（距离、尺寸、数字接收标志）

接收数据包结构：
```cpp
struct ReceivePacket {
    uint8_t header = 0xFF;
    uint8_t number;       // 目标数字
    uint8_t end = 0xFA;
} __attribute__((packed));
```

发送数据包结构：
```cpp
struct SendPacket {
    uint8_t header = 0xFF;
    float depth;          // 距离（mm）
    float length;         // 尺寸（mm）
    float is_received;    // 数字接收标志
    uint8_t end = 0xFA;
    uint16_t checksum;    // CRC16 校验
} __attribute__((packed));
```

---

## 模块详解

### SegmentDetector

**文件：** `segmentDetector.py`

通用的 YOLO 分割检测器封装，用于板子检测。

```python
class SegmentDetector:
    def __init__(self, model_path: str, conf: float = 0.5, iou: float = 0.5)
    def detect(self, image: np.ndarray) -> List[Dict]:
        # 返回：[{"xyxy": [...], "conf": 0.95, "cls_id": 0, "cls_name": "board", "polygon": np.ndarray}]
```

### ShapeDetector

**文件：** `shapeDetector.py`

专为三种形状类别定制的 YOLO 分割模型封装。

```python
class ShapeDetector:
    cls_map = {0: ("circle", "red"), 1: ("square", "blue"), 2: ("triangle", "green")}

    def __init__(self, model_path: str, conf: float = 0.5, iou: float = 0.5)
    def detect(self, image: np.ndarray) -> Dict:
        # 返回结构化字典，包含 circle、square（列表）、triangle
    def visualize(self, image: np.ndarray, detections: Dict) -> np.ndarray
```

### SubImageProcessor

**文件：** `subImageProcesser.py`

使用分割掩码从原图中提取和管理子图。

```python
class SubImageProcessor:
    def extract_subimages(self, frame: np.ndarray, detections: List[Dict]) -> List[Dict]
    def get_subimages(self) -> List[np.ndarray]
    def restore_coordinates(self, det: Dict, polygon: np.ndarray) -> np.ndarray
    def extract_rectangular_subimage(self, subimg: np.ndarray, polygon: np.ndarray) -> np.ndarray
    def extract_rectangle_features(self, polygon: np.ndarray) -> np.ndarray  # 4 个角点
```

### GeometryFeatureProcessor

**文件：** `featureProcesser.py`

使用经典 CV 技术进行高精度几何特征提取（1599 行）。

```python
class GeometryFeatureProcessor:
    gray_image: np.ndarray  # 使用前必须设置

    def extract_board_features(self, polygon: np.ndarray) -> np.ndarray    # 4 个有序角点
    def extract_square_features(self, polygon: np.ndarray) -> Tuple[np.ndarray, float]  # 角点，边长
    def extract_rectangle_features(self, polygon: np.ndarray) -> np.ndarray  # 4 个有序角点
    def extract_triangle_features(self, polygon: np.ndarray) -> Tuple[np.ndarray, float]  # 顶点，边长
    def extract_circle_features(self, polygon: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[float]]  # 中心，直径
    def extract_ellipse_features(self, polygon: np.ndarray) -> Tuple  # 椭圆轴端点
    def draw_ordered_corners(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray
```

### PnPSolver

**文件：** `pnpSolver.py`

使用 OpenCV 的 `solvePnP` 进行 3D 位姿估计。

```python
class PnPSolver:
    def __init__(self, camera_matrix: np.ndarray, dist_coeffs: np.ndarray,
                 method: int = cv2.SOLVEPNP_ITERATIVE)
    def solve(self, object_points: np.ndarray, image_points: np.ndarray) -> Tuple[bool, np.ndarray, np.ndarray]
    @staticmethod
    def rotation_vector_to_matrix(rvec: np.ndarray) -> np.ndarray
    @staticmethod
    def calculate_reprojection_error(object_pts, image_pts, rvec, tvec, camera_mat, dist) -> float
    def visualize_pose(self, image: np.ndarray, rvec: np.ndarray, tvec: np.ndarray) -> np.ndarray
```

### HomographyTransformer

**文件：** `transformer.py`

像素坐标与真实世界坐标间的透视变换。

```python
class HomographyTransformer:
    def __init__(self, src_points: np.ndarray, dst_points: np.ndarray)
    def update_src_points(self, src_points: np.ndarray) -> 'HomographyTransformer'
    def update_dst_points(self, dst_points: np.ndarray) -> 'HomographyTransformer'
    def recompute_homography(self) -> bool
    def transform_point(self, point: np.ndarray) -> np.ndarray
    def transform_features(self, features: np.ndarray) -> np.ndarray
    def transform_vector_angle(self, angle: float) -> float
    def warp_frame(self, image: np.ndarray) -> np.ndarray
```

### NumberClassifier

**文件：** `numberClassify.py`

YOLOv8 分类模型封装，用于数字识别。

```python
class NumberClassifier:
    def __init__(self, model_path: str, conf_threshold: float = 0.5, device: str = "auto")
    def detect(self, image: np.ndarray, set_number: Optional[int] = None) -> Optional[Union[float, Tuple[int, float]]]
    def visualize(self, image: np.ndarray, number: int) -> np.ndarray
```

### CameraCalibrator

**文件：** `calibration.py`

基于棋盘格的相机标定工具。

```python
class CameraCalibrator:
    def __init__(self, chessboard_size: Tuple[int, int] = (9, 6), square_size: float = 25.0)
    def calibrate(self, images: List[np.ndarray]) -> Tuple[bool, np.ndarray, np.ndarray]
    def calculate_board_distance(self, image: np.ndarray, board_corners: np.ndarray) -> float
```

---

## 测试模块

### 完整流水线测试

**文件：** `test_pipeline.py`

一个全面的独立测试脚本，在不依赖 ROS 2 的情况下对单张图片运行完整的检测流水线。演示系统的每个阶段。

**使用方法：**
```bash
cd detect_shape
python test_pipeline.py
```

**测试内容：**
1. 板子分割（`board.pt`）
2. 子图提取
3. 形状检测（`shape.pt`）
4. 板子角点提取
5. PnP 距离计算
6. 单应变换到真实世界坐标
7. 圆形直径、正方形边长、三角形边长测量

**预期输出：** 带所有检测结果、测量值和距离信息的标注图片 `test_result.jpg`。

```python
#!/usr/bin/env python3
"""
完整形状检测流水线的独立测试脚本。
加载 test_img_all.jpg 并执行完整检测流水线：
  板子检测 -> 子图提取 -> 形状检测 -> 特征提取 -> PnP 测距 -> 单应变换
结果绘制在图片上并保存为 test_result.jpg

使用方法：
    cd detect_shape
    python test_pipeline.py
"""

import os, sys, cv2, numpy as np

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PKG_PATH = os.path.join(PROJECT_ROOT, "workdir", "ros2_ws", "src", "shape_detector")
sys.path.insert(0, PKG_PATH)

from shape_detector.transformer import HomographyTransformer
from shape_detector.utils import load_points_from_yaml
from shape_detector.segmentDetector import SegmentDetector
from shape_detector.subImageProcesser import SubImageProcessor
from shape_detector.shapeDetector import ShapeDetector
from shape_detector.featureProcesser import GeometryFeatureProcessor
from shape_detector.pnpSolver import PnPSolver

# --- 路径配置 ---
MODEL_DIR = os.path.join(PROJECT_ROOT, "workdir", "ros2_ws", "model")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "workdir", "ros2_ws", "config")
TEST_IMAGE = os.path.join(PROJECT_ROOT, "test_img_all.jpg")
OUTPUT_IMAGE = os.path.join(PROJECT_ROOT, "test_result.jpg")

BOARD_MODEL  = os.path.join(MODEL_DIR, "board.pt")
SHAPE_MODEL  = os.path.join(MODEL_DIR, "shape.pt")
SRC_PTS = os.path.join(CONFIG_DIR, "src_pts.yaml")
DST_PTS = os.path.join(CONFIG_DIR, "dst_pts.yaml")

# --- 加载测试图片 ---
frame = cv2.imread(TEST_IMAGE)
annotated = frame.copy()

# --- 第1步：板子分割 ---
segment_detector = SegmentDetector(model_path=BOARD_MODEL, conf=0.5)
detections = segment_detector.detect(frame)

# --- 第2步：子图提取 ---
subimage_processor = SubImageProcessor()
detections = subimage_processor.extract_subimages(frame, detections)
subimages = subimage_processor.get_subimages()

# --- 初始化各处理器 ---
shape_detector = ShapeDetector(model_path=SHAPE_MODEL)
feature_processor = GeometryFeatureProcessor()
camera_matrix = np.array(
    [[1728.27186, 0.0, 569.30447],
     [0.0, 1729.86488, 418.90675],
     [0.0, 0.0, 1.0]], dtype=np.float32
)
dist_coeffs = np.array(
    [-0.080040, 0.468967, -0.012946, -0.002907, 0.000000], dtype=np.float32
)
pnp_solver = PnPSolver(camera_matrix, dist_coeffs, method=cv2.SOLVEPNP_EPNP)
src_pts = load_points_from_yaml(SRC_PTS)
dst_pts = load_points_from_yaml(DST_PTS)
homography_transformer = HomographyTransformer(src_points=src_pts, dst_points=dst_pts)

# --- 处理每个板子检测结果 ---
for det, subimg in zip(detections, subimages):
    # 转换为灰度图
    gray_subimg = cv2.cvtColor(subimg[:,:,:3], cv2.COLOR_BGR2GRAY)
    feature_processor.gray_image = gray_subimg

    # 提取板子角点
    board_corners = feature_processor.extract_rectangle_features(det["polygon"])

    # PnP 距离计算
    object_points = np.array(
        [[0.0, 0.0, 0.0], [210.0, 0.0, 0.0],
         [210.0, 297.0, 0.0], [0.0, 297.0, 0.0]], dtype=np.float32
    )
    success, rvec, tvec = pnp_solver.solve(object_points, board_corners)
    distance = float(tvec[2][0])  # 单位 mm

    # 用实际板子角点更新单应矩阵
    homography_transformer.update_src_points(board_corners).recompute_homography()

    # 在子图上检测形状
    sub_detections = shape_detector.detect(subimg)

    # 提取各形状的特征
    for cls_name, data in sub_detections.items():
        if data is None or (isinstance(data, list) and len(data) == 0):
            continue

        if cls_name == "circle":
            restored = subimage_processor.restore_coordinates(det, data["polygon"])
            transformed = homography_transformer.transform_features(restored)
            _, real_diameter = feature_processor.extract_circle_features(transformed)
            print(f"圆形直径: {real_diameter/10:.1f} cm")

        elif cls_name == "square":
            for square in data:
                restored = subimage_processor.restore_coordinates(det, square["polygon"])
                transformed = homography_transformer.transform_features(restored)
                _, real_length = feature_processor.extract_square_features(transformed)
                print(f"正方形边长: {real_length/10:.1f} cm")

        elif cls_name == "triangle":
            restored = subimage_processor.restore_coordinates(det, data["polygon"])
            transformed = homography_transformer.transform_features(restored)
            _, real_length = feature_processor.extract_triangle_features(transformed)
            print(f"三角形边长: {real_length/10:.1f} cm")

cv2.imwrite(OUTPUT_IMAGE, annotated)
```

### 数字分类器测试

**文件：** `test/test_number.py`

独立测试基于 YOLO 的数字分类器。

**使用方法：**
```bash
cd detect_shape
python test/test_number.py
```

**测试内容：**
- 加载 `number.pt` 模型
- 对 `assets/test_number.jpg` 运行分类
- 输出标注后的图片到 `test_number_result.jpg`

```python
import cv2
import numpy as np
from ultralytics import YOLO

class NumberClassifier:
    def __init__(self, model_path="yolov8n-cls.pt", conf_threshold=0.5, device="auto"):
        if device == "auto":
            try:
                import torch
                if torch.cuda.is_available() and torch.cuda.device_count() > 0:
                    device = "cuda:0"
                else:
                    device = "cpu"
            except Exception:
                device = "cpu"

        self.model = YOLO(model_path).float() if device == "cpu" else YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.device = device
        self.class_names = {i: str(i) for i in range(10)}  # 数字 0-9

    def detect(self, image):
        """执行数字分类推理"""
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise ValueError(f"无法读取图像: {image}")

        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.model(image, verbose=False, device=self.device, imgsz=224)

        if results and hasattr(results[0], "probs"):
            probs = results[0].probs.data.cpu().numpy()
            top1_index = np.argmax(probs)
            confidence = probs[top1_index]

            if confidence >= self.conf_threshold:
                return int(self.class_names[top1_index]), float(confidence)
        return None

    def visualize(self, image, prediction=None):
        """可视化分类结果"""
        display_img = image.copy()
        if prediction is not None:
            digit, conf = prediction
            label = f"数字: {digit} (置信度: {conf:.2f})"
            cv2.putText(display_img, label, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return display_img


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    model_path = os.path.join(project_root, "workdir/ros2_ws/model/number.pt")
    test_image_path = os.path.join(project_root, "assets/test_number.jpg")
    output_image_path = os.path.join(project_root, "test_number_result.jpg")

    number_classifier = NumberClassifier(model_path=model_path)
    original_image = cv2.imread(test_image_path)
    if original_image is None:
        print(f"[ERROR] 无法读取图像: {test_image_path}")
        sys.exit(1)
    print(f"[OK]   加载图像: {test_image_path} ({original_image.shape[1]}x{original_image.shape[0]})")

    result = number_classifier.detect(test_image_path)
    print(f"识别结果: {result}")

    if result is not None:
        digit, conf = result
        result_image = number_classifier.visualize(original_image, result)
        cv2.imwrite(output_image_path, result_image)
        print(f"[OK]   结果图片已保存: {output_image_path}")
    else:
        print("[WARN] 未检测到有效数字（置信度低于阈值）")
```

### 串口驱动测试

**文件：** `workdir/ros2_ws/src/rm_serial_driver/test/parseSendPacket.py`

串口通信数据包解析测试工具。连接 `/dev/ttyUSB0`（115200 波特率），解析带 CRC16 校验的传入数据包。

---

## 工具脚本

### 测试图生成器

这些脚本生成带真实尺寸标注的测试图片，用于验证测量精度：

| 脚本 | 生成内容 | 输出目录 |
|------|---------|---------|
| `utils/gen_pic_base.py` | 带黑色边框的 A4 页面 | `a4_with_border.jpg` |
| `utils/gen_pic_circle.py` | 直径 10–16 cm 的圆形在 A4 上 | `tmp/circle/` |
| `utils/gen_pic_square.py` | 边长 10–16 cm 的正方形在 A4 上 | `tmp/square/` |
| `utils/gen_pic_triangle.py` | 边长 10–16 cm 的三角形在 A4 上 | `tmp/triangle/` |

所有图片均为 600 DPI，确保精准的真实尺寸参照。

### 视频录制工具

ROS 2 节点，按键触发录制视频流：

| 脚本 | 订阅话题 | 输出目录 |
|------|---------|---------|
| `utils/save_all.py` | `/image_raw` | `assets/` |
| `utils/save_sub.py` | `/result_sub_origin_image` | `assets_sub/` |
| `utils/save_sub_square.py` | `/sub_square_image` | `assets_sub_square/` |

按 `s` 键开始/停止录制。

### 标定工具

| 脚本 | 作用 |
|------|------|
| `utils/calibration_pts.py` | 交互式单应点选取器（点击定义源点，保存到 `src_pts.yaml`） |
| `utils/test_h.py` | 单应矩阵计算与验证 |

---

## 模型文件

位于 `workdir/ros2_ws/model/`：

| 模型 | 类型 | 任务 | 类别 |
|------|------|------|------|
| `board.pt` | YOLOv8-seg | 分割 | board（带黑框 A4 纸） |
| `shape.pt` | YOLOv8-seg | 分割 | circle, square, triangle |
| `number.pt` | YOLOv8-cls | 分类 | 数字 0–9 |
| `laser.pt` | YOLOv8-seg | 分割 | 激光点（红色 + 紫色） |
| `laser_red.pt` | YOLOv8-seg | 分割 | 红色激光点 |

所有模型使用 YOLOv8 训练。目录中的 `.pt.bak` 文件是训练迭代的备份，可以安全删除。

---

## 配置文件

### 相机标定

**文件：** `config/camera_info.yaml`

```
分辨率: 1280x720
相机内参矩阵:
  fx: 438.78  fy: 437.30
  cx: 305.59  cy: 243.74
畸变系数: [-0.362, 0.111, 0.001, 0.001, 0]
```

**文件：** `config/params_1.yaml`（USB 相机参数）
```yaml
camera_name: test_camera
video_device: /dev/video2
pixel_format: mjpeg
width: 1280
height: 720
framerate: 30.0
```

### 单应变换点

**源点**（图像上 A4 纸角点的像素坐标）：
```yaml
# config/src_pts.yaml
points:
  - [96, 62]     # 左上
  - [509, 101]   # 右上
  - [504, 403]   # 右下
  - [59, 389]    # 左下
```

**目标点**（对应的真实世界 A4 尺寸，单位 mm）：
```yaml
# config/dst_pts.yaml
points:
  - [0, 0]       # 左上
  - [210, 0]     # 右上（210mm 宽）
  - [210, 297]   # 右下（297mm 高）
  - [0, 297]     # 左下
```

---

## 主检测流水线流程

无论作为 ROS 2 节点运行还是独立测试，每帧图像的处理顺序如下：

```
┌─────────────────────────────────────────────────────────┐
│                    摄像头帧                              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  1. 板子分割（SegmentDetector）                          │
│     YOLOv8-seg：检测带黑边框的 A4 纸                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  2. 子图提取（SubImageProcessor）                        │
│     裁剪板子区域，创建带 Alpha 掩码的 RGBA               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  3. 形状检测（ShapeDetector）                            │
│     YOLOv8-seg：检测圆形/正方形/三角形                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  4. 板子角点提取（GeometryFeatureProcessor）             │
│     亚像素精度的矩形角点                                 │
└──────────┬──────────────────────────────────────────┬────┘
           │                                          │
           ▼                                          ▼
┌─────────────────────┐              ┌──────────────────────────┐
│  5a. PnP 测距       │              │  5b. 更新单应矩阵        │
│     相机到板子距离   │              │     像素→真实世界坐标    │
│     （单位 mm）      │              │     使用实际检测角点      │
└─────────────────────┘              └──────────┬───────────────┘
                                                 │
                                                 ▼
                        ┌────────────────────────────────────────┐
                        │  6. 特征提取（真实世界坐标）             │
                        │     圆形：椭圆拟合 → 直径               │
                        │     正方形：直线拟合 → 边长             │
                        │     三角形：最大面积 → 边长              │
                        └────────────────┬───────────────────────┘
                                         │
                                         ▼
                        ┌────────────────────────────────────────┐
                        │  7. 串口输出                           │
                        │     depth + length → 下位机 via UART   │
                        │     （条件触发：数字分类模式）           │
                        └────────────────────────────────────────┘
```

---

## 开发指南

### 添加新形状

1. 收集训练图片并用 YOLO 分割格式标注
2. 训练新的 YOLOv8-seg 模型：
   ```bash
   yolo segment train data=shapes.yaml model=yolov8n-seg.pt epochs=100
   ```
3. 更新 `shapeDetector.py` 中的 `cls_map`
4. 在 `GeometryFeatureProcessor` 中添加特征提取方法
5. 在 `shape_detector_node.py` 的 `_feature_process()` 中添加处理逻辑

### 不依赖 ROS 2 运行

使用 `test_pipeline.py` 进行独立测试，不需要 ROS 2 依赖。它加载相同的模块并运行相同的流水线。

---

## 许可证

本项目基于 `LICENSE` 文件中指定的条款开源。
