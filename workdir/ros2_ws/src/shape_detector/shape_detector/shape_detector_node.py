import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
from custom_msgs.msg import DetectResult, ReceivedData

from .transformer import HomographyTransformer
from .utils import load_points_from_yaml
from .segmentDetector import SegmentDetector
from .subImageProcesser import SubImageProcessor
from .shapeDetector import ShapeDetector
from .featureProcesser import GeometryFeatureProcessor
from .pnpSolver import PnPSolver
from .numberClassify import NumberClassifier


class ShapeDetectorNode(Node):
    def __init__(self):
        super().__init__("shape_detector_node")
        self.bridge = CvBridge()

        self.detect_result = DetectResult()

        # ROS2参数声明
        self.declare_parameter("board_model_path", "./model/board.pt")
        self.declare_parameter("shape_model_path", "./model/shape.pt")
        self.declare_parameter("number_model_path", "./model/number.pt")
        self.declare_parameter("hmin", 131)
        self.declare_parameter("hmax", 178)
        self.declare_parameter("smin", 3)
        self.declare_parameter("smax", 255)
        self.declare_parameter("vmin", 202)
        self.declare_parameter("vmax", 255)

        self.declare_parameter("hmin_no_black", 154)
        self.declare_parameter("hmax_no_black", 179)
        self.declare_parameter("smin_no_black", 17)
        self.declare_parameter("smax_no_black", 255)
        self.declare_parameter("vmin_no_black", 27)
        self.declare_parameter("vmax_no_black", 255)

        # 获取参数值
        board_model_path = self.get_parameter("board_model_path").value
        shape_model_path = self.get_parameter("shape_model_path").value
        number_model_path = self.get_parameter("number_model_path").value
        # hsv_params = {
        #     "hmin": self.get_parameter("hmin").value,
        #     "hmax": self.get_parameter("hmax").value,
        #     "smin": self.get_parameter("smin").value,
        #     "smax": self.get_parameter("smax").value,
        #     "vmin": self.get_parameter("vmin").value,
        #     "vmax": self.get_parameter("vmax").value,
        # }
        # hsv_on_black_params = {
        #     "hmin": self.get_parameter("hmin_no_black").value,
        #     "hmax": self.get_parameter("hmax_no_black").value,
        #     "smin": self.get_parameter("smin_no_black").value,
        #     "smax": self.get_parameter("smax_no_black").value,
        #     "vmin": self.get_parameter("vmin_no_black").value,
        #     "vmax": self.get_parameter("vmax_no_black").value,
        # }

        # 初始化处理模块
        self.segment_detector = SegmentDetector(
            model_path=board_model_path, conf=0.5)
        self.subimage_processor = SubImageProcessor()
        self.shape_detector = ShapeDetector(model_path=shape_model_path)
        self.feature_processor = GeometryFeatureProcessor()
        # 参数声明
        src_pts = load_points_from_yaml("./config/src_pts.yaml")
        dst_pts = load_points_from_yaml("./config/dst_pts.yaml")
        self.homography_transformer = HomographyTransformer(
            src_points=src_pts, dst_points=dst_pts
        )
        self.number_classifier = NumberClassifier(model_path=number_model_path)
        # 初始化相机参数
        camera_matrix = np.array(
            [
                [1728.27186, 0.0, 569.30447],
                [0.0, 1729.86488, 418.90675],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )

        dist_coeffs = np.array(
            [-0.080040, 0.468967, -0.012946, -0.002907, 0.000000], dtype=np.float32
        )
        # 创建PnP求解器实例
        self.pnp_solver = PnPSolver(
            camera_matrix, dist_coeffs, method=cv2.SOLVEPNP_EPNP
        )

        # 创建订阅者和发布者
        # sub
        self.received_data_sub = self.create_subscription(
            ReceivedData, "/received_data", self.received_data_callback, 10
        )
        self.subscription = self.create_subscription(
            Image, "/image_raw", self.image_callback, 10  # 队列大小
        )
        self.result_image_pub = self.create_publisher(
            Image, "result_image", 10)
        self.result_sub_image_pub = self.create_publisher(
            Image, "result_sub_image", 10)

        self.result_sub_origin_image_pub = self.create_publisher(
            Image, "result_sub_origin_image", 10
        )
        # self.debug_image_pub = self.create_publisher(Image, "debug_image", 10)
        self.detect_result_pub = self.create_publisher(
            DetectResult, "detect_result", 10
        )

        self.get_logger().info("激光检测节点已启动，等待图像输入...")
        self.fps = 0
        self.last_time = time.time()

        self.is_number_cls_mode = False
        self.number = None

    def received_data_callback(self, msg):
        if self.is_number_cls_mode == False:
            self.is_number_cls_mode = True
        self.number = msg.number
        self.detect_result.is_received = float(1)
        self.get_logger().info(f"进入数字检测模式, number: {msg.number}")

    def image_callback(self, msg):
        """处理传入的图像消息"""
        try:
            # 转换ROS图像消息为OpenCV格式
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"传入图像转换失败: {str(e)}")
            return

        # 执行处理流程
        self.process_frame(cv_image, msg.header)

        # 更新FPS
        current_time = time.time()
        self.fps = 0.9 * self.fps + 0.1 / \
            (current_time - self.last_time + 1e-5)
        self.last_time = current_time
        self.get_logger().debug(f"处理FPS: {self.fps:.1f}")

    def number_cls_callback(self, sub_square_image):
        # 输入图片，输出数字
        self.get_logger().info("进行数字检测")

        # 进行数字分类
        result = self.number_classifier.detect(sub_square_image)
        if result is not None:
            number = result[0]
            return int(number) == int(self.number)
        return False

    def process_frame(self, frame, header):
        """处理单帧图像并发布结果"""

        self.detect_result.header = header
        # 执行分割检测
        detections = self.segment_detector.detect(frame)

        # 提取子图,更新单应矩阵
        if detections:
            detections = self.subimage_processor.extract_subimages(
                frame, detections)

        # 创建结果图像
        result_image = frame.copy()

        # # TODO:
        # # for debug
        # debug_image = frame.copy()
        # red_pos, purple_pos = self.laser_detector.detect(debug_image)
        #
        # if red_pos or purple_pos:
        #     debug_image = self.laser_detector.visualize(
        #         debug_image, red_pos, purple_pos
        #     )
        # # debug图像
        # if debug_image is not None:
        #     try:
        #         debug_image_msg = self.bridge.cv2_to_imgmsg(
        #             debug_image, encoding="bgra8"
        #         )
        #         debug_image_msg.header = header
        #         self.debug_image_pub.publish(debug_image_msg)
        #     except Exception as e:
        #         self.get_logger().error(f"debug图像发布失败: {str(e)}")
        #
        # 绘制检测结果
        overlay = np.zeros_like(frame, dtype=np.uint8)
        for det in detections:
            color = self.segment_detector.colors[
                det["cls_id"] % len(self.segment_detector.colors)
            ]
            cv2.fillPoly(overlay, [det["polygon"]], color)
            x1, y1, x2, y2 = map(int, det["xyxy"])
            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
            label = f"{det['cls_name']} {det['conf']:.2f}"
            cv2.putText(
                result_image,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        # 融合覆盖层
        cv2.addWeighted(overlay, 0.4, result_image, 0.6, 0, result_image)

        # 添加FPS显示
        cv2.putText(
            result_image,
            f"FPS: {self.fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # 处理子图
        # std_msgs/Header header
        # float32 depth
        # float32 length

        # 处理子图
        subimages = self.subimage_processor.get_subimages()
        for i, subimg in enumerate(subimages):
            if subimg is not None:
                try:
                    result_msg_ = self.bridge.cv2_to_imgmsg(
                        subimg, encoding="bgra8")
                    result_msg_.header = header
                    self.result_sub_origin_image_pub.publish(result_msg_)
                except Exception as e:
                    self.get_logger().error(f"子图图像发布失败: {str(e)}")
                if detections is not None and i < len(detections):
                    try:
                        # TODO:
                        # shape_detect
                        sub_detections = self.shape_detector.detect(subimg)
                        result_img = None
                        if sub_detections is not None:
                            result_img = self.shape_detector.visualize(
                                subimg, sub_detections
                            )
                            board_corners = (
                                self.feature_processor.extract_rectangle_features(
                                    detections[i]["polygon"]
                                )
                            )
                            object_points = np.array(
                                [
                                    [0.0, 0.0, 0.0],
                                    [210, 0.0, 0.0],
                                    [210, 297, 0.0],
                                    [0, 297, 0.0],
                                ]
                            )
                            # 根据黑框的四个角点计算距离
                            success, rvec, tvec = self.pnp_solver.solve(
                                object_points, board_corners
                            )
                            distance = tvec[2][0]
                            self.get_logger().info(f"距离: {distance}")
                            self.detect_result.depth = float(distance)
                            result_image = self.feature_processor.draw_ordered_corners(
                                result_image, board_corners
                            )
                            try:
                                self.homography_transformer.update_src_points(
                                    board_corners
                                )
                                self.homography_transformer.recompute_homography()
                                # 更新一次单应矩阵
                                # pixel_features用于显示图像，real_features用于计算边长
                                pixel_features, real_features = self._feature_process(
                                    sub_detections, detections[i], subimg
                                )

                            except Exception as e:
                                self.get_logger().error(f"提取子图特征失败: {str(e)}")

                        # 发布结果图像
                        if result_img is not None:
                            try:
                                result_sub_msg = self.bridge.cv2_to_imgmsg(
                                    result_img, encoding="bgra8"
                                )
                                result_sub_msg.header = header
                                self.result_sub_image_pub.publish(
                                    result_sub_msg)
                            except Exception as e:
                                self.get_logger().error(
                                    f"检测子图结果图像发布失败: {str(e)}"
                                )

                    except Exception as e:
                        self.get_logger().error(f"shape_detect失败: {str(e)}")

        # 发布结果图像
        try:
            result_msg = self.bridge.cv2_to_imgmsg(
                result_image, encoding="bgr8")
            result_msg.header = header
            self.result_image_pub.publish(result_msg)
        except Exception as e:
            self.get_logger().error(f"检测黑框结果图像发布失败: {str(e)}")

        # 发布检测结果
        self.detect_result_pub.publish(self.detect_result)

    def _feature_process(self, sub_detections, det, subimg):
        pixel_features = {}
        real_features = {}
        for cls_id in self.shape_detector.cls_map:
            cls_name, _ = self.shape_detector.cls_map[cls_id]
            if sub_detections[cls_name] is not None:
                self.get_logger().info(f"detect {cls_name}")
                pos, radius, length = None, None, None
                if cls_name == "circle":
                    pos, radius = self.feature_processor.extract_circle_features(
                        sub_detections[cls_name]["polygon"]
                    )
                    # for sub
                    pixel_features[cls_name] = (pos, radius)

                    # for whole
                    real_pos, radius = self.feature_processor.extract_circle_features(
                        self.homography_transformer.transform_features(
                            self.subimage_processor.restore_coordinates(
                                det, sub_detections[cls_name]["polygon"]
                            )
                        )
                    )
                    real_features[cls_name] = (real_pos, radius)
                    self.get_logger().info(f"radius: {radius}")
                    self.detect_result.length = float(radius)

                elif cls_name == "square":
                    # TODO: 处理数字
                    if self.is_number_cls_mode:
                        squares = sub_detections[cls_name]
                        if not squares:  # 如果没有检测到方形，则跳过
                            continue
                        # 提取方形子图
                        is_find_set_number = False
                        for square in squares:
                            sub_square_image = (
                                self.subimage_processor.extract_rectangular_subimage(
                                    subimg, square["polygon"], aspect_ratio=2.0
                                )
                            )
                            is_find_set_number = self.number_cls_callback(
                                sub_square_image
                            )

                            if is_find_set_number:
                                # 提取当前方形的特征
                                pixel_corners, pixel_length = (
                                    self.feature_processor.extract_square_features(
                                        square["polygon"]
                                    )
                                )
                                restored_polygon = (
                                    self.subimage_processor.restore_coordinates(
                                        det, square["polygon"]
                                    )
                                )
                                # 应用单应变换，将坐标转换到真实世界坐标系
                                transformed_polygon = (
                                    self.homography_transformer.transform_features(
                                        restored_polygon
                                    )
                                )
                                # 在真实世界坐标系中提取方形的特征
                                real_corners, real_length = (
                                    self.feature_processor.extract_square_features(
                                        transformed_polygon
                                    )
                                )

                                pixel_features[cls_name] = (
                                    pixel_corners, pixel_length)
                                real_features[cls_name] = (
                                    real_corners, real_length)
                                self.get_logger().info(
                                    f"true number square length: {real_length}"
                                )
                                self.detect_result.length = float(real_length)
                                break
                    else:
                        # 特殊处理square类型
                        squares = sub_detections[cls_name]
                        if not squares:  # 如果没有检测到方形，则跳过
                            continue

                        min_length = float("inf")  # 初始化为极大值
                        min_square = None
                        min_real_corners = None

                        # 遍历所有检测到的方形
                        for square in squares:
                            # 提取当前方形的特征
                            pixel_corners, pixel_length = (
                                self.feature_processor.extract_square_features(
                                    square["polygon"]
                                )
                            )

                            # 恢复坐标到原图（通过det，即黑框的检测信息）
                            restored_polygon = (
                                self.subimage_processor.restore_coordinates(
                                    det, square["polygon"]
                                )
                            )

                            # 应用单应变换，将坐标转换到真实世界坐标系
                            transformed_polygon = (
                                self.homography_transformer.transform_features(
                                    restored_polygon
                                )
                            )

                            # 在真实世界坐标系中提取方形的特征
                            real_corners, real_length = (
                                self.feature_processor.extract_square_features(
                                    transformed_polygon
                                )
                            )

                            # 更新最小边长和对应的方形
                            if real_length < min_length:
                                min_length = real_length
                                min_square = square
                                min_real_corners = real_corners
                                min_pixel_corners = pixel_corners

                        # 保存最小方形的特征
                        pixel_features[cls_name] = (
                            min_pixel_corners, min_length)
                        real_features[cls_name] = (
                            min_real_corners, min_length)
                        self.get_logger().info(
                            f"Min square length: {min_length}")
                        self.detect_result.length = float(min_length)

                elif cls_name == "triangle":
                    pixel_features[cls_name] = (
                        self.feature_processor.extract_triangle_features(
                            sub_detections[cls_name]["polygon"]
                        )
                    )
                    real_coners, length = (
                        self.feature_processor.extract_triangle_features(
                            self.homography_transformer.transform_features(
                                self.subimage_processor.restore_coordinates(
                                    det, sub_detections[cls_name]["polygon"]
                                )
                            )
                        )
                    )
                    real_features[cls_name] = (real_coners, length)
                    self.get_logger().info(f"length: {length}")
                    self.detect_result.length = float(length)

        return pixel_features, real_features

    # def _feature_process(self, sub_detections, det):
    #     pixel_features = {}
    #     real_features = {}
    #     for cls_id in self.shape_detector.cls_map:
    #         cls_name, _ = self.shape_detector.cls_map[cls_id]
    #         if sub_detections[cls_name] is not None:
    #             self.get_logger().info(f"detect {cls_name}")
    #             pos, radius, length = None, None, None
    #             if cls_name == "circle":
    #                 pos, radius = self.feature_processor.extract_circle_features(
    #                     sub_detections[cls_name]["polygon"]
    #                 )
    #                 # for sub
    #                 pixel_features[cls_name] = (pos, radius)
    #
    #                 # for whole
    #                 real_pos, radius = self.feature_processor.extract_circle_features(
    #                     self.homography_transformer.transform_features(
    #                         self.subimage_processor.restore_coordinates(
    #                             det, sub_detections[cls_name]["polygon"]
    #                         )
    #                     )
    #                 )
    #                 real_features[cls_name] = (real_pos, radius)
    #                 self.get_logger().info(f"radius: {radius}")
    #                 self.detect_result.length = float(radius)
    #
    #             elif cls_name == "square":
    #                 pixel_features[cls_name] = (
    #                     self.feature_processor.extract_square_features(
    #                         sub_detections[cls_name]["polygon"]
    #                     )
    #                 )
    #                 real_coners, length = (
    #                     self.feature_processor.extract_square_features(
    #                         self.homography_transformer.transform_features(
    #                             self.subimage_processor.restore_coordinates(
    #                                 det, sub_detections[cls_name]["polygon"]
    #                             )
    #                         )
    #                     )
    #                 )
    #                 real_features[cls_name] = (real_coners, length)
    #                 self.get_logger().info(f"length: {length}")
    #                 self.detect_result.length = float(length)
    #             elif cls_name == "triangle":
    #                 pixel_features[cls_name] = (
    #                     self.feature_processor.extract_triangle_features(
    #                         sub_detections[cls_name]["polygon"]
    #                     )
    #                 )
    #                 real_coners, length = (
    #                     self.feature_processor.extract_triangle_features(
    #                         self.homography_transformer.transform_features(
    #                             self.subimage_processor.restore_coordinates(
    #                                 det, sub_detections[cls_name]["polygon"]
    #                             )
    #                         )
    #                     )
    #                 )
    #                 real_features[cls_name] = (real_coners, length)
    #                 self.get_logger().info(f"length: {length}")
    #                 self.detect_result.length = float(length)
    #     return pixel_features, real_features


def main(args=None):
    rclpy.init(args=args)
    node = ShapeDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
