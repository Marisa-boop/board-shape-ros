# Copyright (c) 2025 Marisa-boop
# SPDX-License-Identifier: MIT

#!/usr/bin/env python3
"""
Standalone test script for the shape detection pipeline.
Loads test_img_all.jpg and runs the full detection pipeline:
  board detection → sub-image extraction → shape detection →
  feature extraction → PnP distance → homography transform

Results are drawn on the image and saved as test_result.jpg

Usage:
    cd /home/linux/projects/docker/detect_shape
    mamba run -n ultralytics python test_pipeline.py
"""

import os
import sys
import cv2
import numpy as np

# ======================================================================
# Path setup – make the ROS 2 shape_detector package importable
# ======================================================================
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

# ======================================================================
# Drawing helpers
# ======================================================================
FONT = cv2.FONT_HERSHEY_SIMPLEX
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

COLORS = {
    "circle": BLUE,
    "square": GREEN,
    "triangle": RED,
}


def draw_text_with_bg(img, text, pos, color=WHITE, bg_color=BLACK,
                       font_scale=0.6, thickness=2):
    """Draw text with a filled background rectangle."""
    (tw, th), _ = cv2.getTextSize(text, FONT, font_scale, thickness)
    x, y = int(pos[0]), int(pos[1])
    cv2.rectangle(img, (x - 2, y - th - 4), (x + tw + 4, y + 4),
                  bg_color, -1)
    cv2.putText(img, text, (x, y), FONT, font_scale, color, thickness, cv2.LINE_AA)


def draw_arrowed_label(img, text, from_pt, to_pt, color=WHITE,
                       font_scale=0.5, thickness=1):
    """Draw a label connected by an arrow line to a point."""
    from_pt = (int(from_pt[0]), int(from_pt[1]))
    to_pt = (int(to_pt[0]), int(to_pt[1]))
    cv2.arrowedLine(img, from_pt, to_pt, color, thickness, tipLength=0.15)
    draw_text_with_bg(img, text, (from_pt[0] + 5, from_pt[1] - 5),
                      color=color, font_scale=font_scale, thickness=thickness)


# ======================================================================
# Paths
# ======================================================================
MODEL_DIR = os.path.join(PROJECT_ROOT, "workdir", "ros2_ws", "model")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "workdir", "ros2_ws", "config")
TEST_IMAGE = os.path.join(PROJECT_ROOT, "test_img_all.jpg")
OUTPUT_IMAGE = os.path.join(PROJECT_ROOT, "test_result.jpg")

BOARD_MODEL = os.path.join(MODEL_DIR, "board.pt")
SHAPE_MODEL = os.path.join(MODEL_DIR, "shape.pt")
SRC_PTS = os.path.join(CONFIG_DIR, "src_pts.yaml")
DST_PTS = os.path.join(CONFIG_DIR, "dst_pts.yaml")

# ======================================================================
# Load image
# ======================================================================
print("=" * 60)
print("Shape Detection Pipeline – Standalone Test")
print("=" * 60)

frame = cv2.imread(TEST_IMAGE)
if frame is None:
    print(f"[ERROR] Could not load test image: {TEST_IMAGE}")
    sys.exit(1)
print(f"[OK]   Loaded image: {TEST_IMAGE} ({frame.shape[1]}x{frame.shape[0]})")

# Make a copy for annotation
annotated = frame.copy()

# ======================================================================
# Step 1 – Board segmentation (detect the A4 black border)
# ======================================================================
print("\n--- Step 1: Board Detection ---")
segment_detector = SegmentDetector(model_path=BOARD_MODEL, conf=0.5)
detections = segment_detector.detect(frame)
print(f"       Found {len(detections)} board detection(s)")

if not detections:
    print("[ERROR] No board detected. Exiting.")
    sys.exit(1)

# Draw board segmentation mask and bounding box on the annotated image
overlay = np.zeros_like(annotated, dtype=np.uint8)
for det in detections:
    color = segment_detector.colors[det["cls_id"] % len(segment_detector.colors)]
    cv2.fillPoly(overlay, [det["polygon"]], color)
    x1, y1, x2, y2 = map(int, det["xyxy"])
    cv2.rectangle(annotated, (x1, y1), (x2, y2), MAGENTA, 2)
    label = f"{det['cls_name']} {det['conf']:.2f}"
    draw_text_with_bg(annotated, label, (x1, y1 - 10), color=MAGENTA)

cv2.addWeighted(overlay, 0.25, annotated, 0.75, 0, annotated)

# ======================================================================
# Step 2 – Sub-image extraction (crop the board region)
# ======================================================================
print("\n--- Step 2: Sub-image Extraction ---")
subimage_processor = SubImageProcessor()
detections = subimage_processor.extract_subimages(frame, detections)
subimages = subimage_processor.get_subimages()
print(f"       Extracted {len(subimages)} sub-image(s)")

# ======================================================================
# Initialise remaining processors
# ======================================================================
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

# ======================================================================
# Step 3 – Process each board detection
# ======================================================================
for i, (det, subimg) in enumerate(zip(detections, subimages)):
    print(f"\n{'=' * 60}")
    print(f"  Board #{i}")
    print(f"{'=' * 60}")

    # Set up the feature processor with the grayscale sub-image
    if subimg.shape[2] == 4:
        gray_subimg = cv2.cvtColor(subimg, cv2.COLOR_BGRA2GRAY)
    elif subimg.shape[2] == 3:
        gray_subimg = cv2.cvtColor(subimg, cv2.COLOR_BGR2GRAY)
    else:
        gray_subimg = subimg[:, :, 0]
    feature_processor.gray_image = gray_subimg

    # ---- 3a. Board corners (for PnP distance) ----
    board_corners = feature_processor.extract_rectangle_features(det["polygon"])
    if board_corners is None:
        print("  [SKIP] Could not extract board corners")
        continue

    print(f"  Board corners (pixel):")
    corner_labels = ["TL", "BL", "BR", "TR"]
    corner_colors = [RED, YELLOW, BLUE, GREEN]
    for label, pt, clr in zip(corner_labels, board_corners, corner_colors):
        print(f"    {label}: ({pt[0]:.1f}, {pt[1]:.1f})")
        # Draw corner circle and label on the annotated image
        pt_int = (int(pt[0]), int(pt[1]))
        cv2.circle(annotated, pt_int, 8, clr, -1)
        draw_text_with_bg(annotated, label, (pt_int[0] + 12, pt_int[1] + 4),
                          color=clr, font_scale=0.7, thickness=2)

    # Draw board outline
    pts = board_corners.reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(annotated, [pts], True, CYAN, 3)

    # ---- 3b. PnP distance ----
    object_points = np.array(
        [[0.0, 0.0, 0.0],
         [210.0, 0.0, 0.0],
         [210.0, 297.0, 0.0],
         [0.0, 297.0, 0.0]], dtype=np.float32
    )
    success, rvec, tvec = pnp_solver.solve(object_points, board_corners)
    if success:
        distance = float(tvec[2][0])
        print(f"\n  >>> Camera-to-board distance: {distance:.1f} mm ({distance/10:.1f} cm)")
        dist_text = f"Distance: {distance:.0f} mm ({distance/10:.1f} cm)"
        draw_text_with_bg(annotated, dist_text, (30, 60), color=GREEN,
                          font_scale=0.8, thickness=2)
    else:
        print("  [WARN] PnP solve failed – distance unknown")
        distance = None

    # ---- 3c. Update homography with actual board corners ----
    homography_transformer.update_src_points(board_corners).recompute_homography()

    # ---- 3d. Shape detection on sub-image ----
    sub_detections = shape_detector.detect(subimg)
    print(f"\n  Shapes detected on board:")
    for cls_name, data in sub_detections.items():
        if cls_name == "square":
            print(f"    square: {len(data)} instance(s)")
        elif data is not None:
            print(f"    {cls_name}: conf={data['conf']:.2f}")
        else:
            print(f"    {cls_name}: none")

    # ---- 3e. Feature extraction for each shape class ----
    print(f"\n  --- Feature Measurements ---")
    for cls_id in shape_detector.cls_map:
        cls_name, _ = shape_detector.cls_map[cls_id]
        data = sub_detections[cls_name]
        if data is None or (isinstance(data, list) and len(data) == 0):
            continue

        color = COLORS.get(cls_name, WHITE)

        if cls_name == "circle":
            pos, diameter = feature_processor.extract_circle_features(data["polygon"])
            print(f"\n  [Circle]")
            print(f"    Pixel diameter: {diameter:.1f} px")

            # Real-world
            restored = subimage_processor.restore_coordinates(det, data["polygon"])
            transformed = homography_transformer.transform_features(restored)
            real_pos, real_diameter = feature_processor.extract_circle_features(transformed)
            if real_pos is not None:
                d_cm = real_diameter / 10
                print(f"    >>> Real diameter: {real_diameter:.1f} mm ({d_cm:.1f} cm)")

                # Draw on annotated image in original coordinates
                restored_poly = subimage_processor.restore_coordinates(det, data["polygon"])
                cv2.polylines(annotated, [restored_poly.reshape(-1, 1, 2).astype(np.int32)],
                              True, color, 3)
                center_orig = (int(restored_poly.mean(axis=0)[0]),
                               int(restored_poly.mean(axis=0)[1]))
                cv2.circle(annotated, center_orig, 5, color, -1)
                label_text = f"Circle diam: {real_diameter:.0f} mm ({d_cm:.1f} cm)"
                draw_arrowed_label(annotated, label_text,
                                   (center_orig[0] + 40, center_orig[1] - 40),
                                   center_orig, color=color)

        elif cls_name == "square":
            for sq_idx, square in enumerate(data):
                print(f"\n  [Square #{sq_idx}]")
                corners, length = feature_processor.extract_square_features(square["polygon"])
                if corners is not None:
                    print(f"    Pixel side length: {length:.1f} px")

                # Real-world
                restored = subimage_processor.restore_coordinates(det, square["polygon"])
                transformed = homography_transformer.transform_features(restored)
                real_corners, real_length = feature_processor.extract_square_features(transformed)
                if real_corners is not None:
                    s_cm = real_length / 10
                    print(f"    >>> Real side length: {real_length:.1f} mm ({s_cm:.1f} cm)")

                    # Draw on annotated image
                    restored_poly = subimage_processor.restore_coordinates(det, square["polygon"])
                    cv2.polylines(annotated, [restored_poly.reshape(-1, 1, 2).astype(np.int32)],
                                  True, color, 3)
                    center_orig = (int(restored_poly.mean(axis=0)[0]),
                                   int(restored_poly.mean(axis=0)[1]))
                    cv2.circle(annotated, center_orig, 5, color, -1)
                    label_text = f"Square #{sq_idx}: {real_length:.0f} mm ({s_cm:.1f} cm)"
                    draw_arrowed_label(annotated, label_text,
                                       (center_orig[0] + 40, center_orig[1] - 40),
                                       center_orig, color=color)

        elif cls_name == "triangle":
            print(f"\n  [Triangle]")
            corners, length = feature_processor.extract_triangle_features(data["polygon"])
            if corners is not None:
                print(f"    Pixel side length: {length:.1f} px")

            # Real-world
            restored = subimage_processor.restore_coordinates(det, data["polygon"])
            transformed = homography_transformer.transform_features(restored)
            real_corners, real_length = feature_processor.extract_triangle_features(transformed)
            if real_corners is not None:
                t_cm = real_length / 10
                print(f"    >>> Real side length: {real_length:.1f} mm ({t_cm:.1f} cm)")

                # Draw on annotated image
                restored_poly = subimage_processor.restore_coordinates(det, data["polygon"])
                cv2.polylines(annotated, [restored_poly.reshape(-1, 1, 2).astype(np.int32)],
                              True, color, 3)
                center_orig = (int(restored_poly.mean(axis=0)[0]),
                               int(restored_poly.mean(axis=0)[1]))
                cv2.circle(annotated, center_orig, 5, color, -1)
                label_text = f"Triangle: {real_length:.0f} mm ({t_cm:.1f} cm)"
                draw_arrowed_label(annotated, label_text,
                                   (center_orig[0] + 40, center_orig[1] - 40),
                                   center_orig, color=color)

# ======================================================================
# Save annotated image
# ======================================================================
cv2.imwrite(OUTPUT_IMAGE, annotated)
print(f"\n{'=' * 60}")
print(f"Annotated result saved to: {OUTPUT_IMAGE}")
print(f"{'=' * 60}")
