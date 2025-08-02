import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading
import os
import time


class VideoRecorderNode(Node):
    def __init__(self, output_dir):
        super().__init__("video_recorder_node")
        self.bridge = CvBridge()
        self.recording = False
        self.frames = []
        self.video_writer = None
        self.frame_size = None
        self.fps = 30  # 默认帧率
        self.output_dir = output_dir  # 新增输出目录[6,7](@ref)

        # 确保输出目录存在[6,7](@ref)
        self.ensure_directory_exists()

        # 订阅图像话题
        self.subscription = self.create_subscription(
            Image,
            "/sub_square_image",
            self.image_callback,
            10,  # 可替换为实际话题名
        )
        self.get_logger().info("节点已启动，等待指令...")
        self.get_logger().info(f"视频将保存至: {os.path.abspath(self.output_dir)}")
        self.get_logger().info("按 's' 开始录制，按 'q' 停止并保存")

        # 启动键盘监听线程
        self.key_thread = threading.Thread(target=self.keyboard_listener)
        self.key_thread.daemon = True
        self.key_thread.start()

    def ensure_directory_exists(self):
        """确保输出目录存在，不存在则创建[6,7](@ref)"""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                self.get_logger().info(
                    f"创建输出目录: {os.path.abspath(self.output_dir)}"
                )
            else:
                self.get_logger().info(
                    f"使用现有目录: {os.path.abspath(self.output_dir)}"
                )
        except OSError as e:
            self.get_logger().error(f"目录创建失败: {str(e)}")
            raise

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            if self.recording:
                # 初始化视频参数（使用第一帧确定分辨率）
                if self.frame_size is None:
                    self.frame_size = (cv_image.shape[1], cv_image.shape[0])
                    self.get_logger().info(
                        f"视频参数: {self.frame_size}@{self.fps}fps")

                # 写入帧
                if self.video_writer:
                    self.video_writer.write(cv_image)
                else:
                    self.frames.append(cv_image)  # 缓冲未初始化的帧

        except Exception as e:
            self.get_logger().error(f"图像转换失败: {str(e)}")

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.frames = []
            self.frame_size = None
            self.get_logger().info("▶️ 开始录制...")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.save_video()
            self.get_logger().info("⏹️ 录制停止，视频已保存")

    def save_video(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # 保存到assets目录[6,7](@ref)
        filename = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # 初始化视频写入器
        self.video_writer = cv2.VideoWriter(
            filename, fourcc, self.fps, self.frame_size)

        # 写入缓冲帧
        for frame in self.frames:
            self.video_writer.write(frame)

        self.video_writer.release()
        self.video_writer = None
        self.frames = []
        self.get_logger().info(f"视频保存至: {os.path.abspath(filename)}")

    def keyboard_listener(self):
        while rclpy.ok():
            key = input().strip().lower()
            if key == "s":
                self.start_recording()
            elif key == "q" and self.recording:
                self.stop_recording()


def main():
    rclpy.init()
    node = VideoRecorderNode("assets_sub_square")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
