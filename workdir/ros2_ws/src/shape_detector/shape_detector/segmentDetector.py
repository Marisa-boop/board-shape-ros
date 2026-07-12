# Copyright (c) 2025 Marisa-boop
# SPDX-License-Identifier: MIT

import numpy as np
from ultralytics import YOLO


# ============================== 分割检测模块 ==============================
class SegmentDetector:
    def __init__(self, model_path, conf=0.5, imgsz=640):
        """
        分割检测器
        :param model_path: 模型路径
        :param conf: 置信度阈值
        :param imgsz: 推理尺寸
        """
        self.model = YOLO(model_path)
        self.model.fuse()
        self.conf = conf
        self.imgsz = imgsz
        self.colors = self._generate_colors(len(self.model.names))

    def _generate_colors(self, n_classes):
        return [np.random.randint(0, 255, 3).tolist() for _ in range(n_classes)]

    def detect(self, frame):
        """执行分割检测"""
        results = self.model.predict(
            frame,
            task="segment",
            imgsz=self.imgsz,
            conf=self.conf,
            device="cuda" if next(
                self.model.model.parameters()).is_cuda else "cpu",
            verbose=False,
        )
        return self._process_detections(results, frame)

    def _process_detections(self, results, frame):
        detections = []
        for result in results:
            if result.masks is None:
                continue

            for mask, box in zip(result.masks.xy, result.boxes):
                if box.conf[0] < self.conf:
                    continue

                cls_id = int(box.cls[0])
                xyxy = box.xyxy[0].cpu().numpy()
                polygon = mask.astype(np.int32)

                detections.append(
                    {
                        "xyxy": xyxy,
                        "conf": float(box.conf[0]),
                        "cls_id": cls_id,
                        "cls_name": self.model.names[cls_id],
                        "polygon": polygon,
                    }
                )

        return detections
