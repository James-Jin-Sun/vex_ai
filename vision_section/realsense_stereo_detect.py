"""
Intel RealSense D455 – RGB YOLO Detection with Depth
=====================================================
Streams the RGB colour camera + aligned depth.
Runs YOLO (best.pt) on the colour frame and overlays:
  • Bounding boxes & class labels
  • Per-detection depth (m) sampled from the aligned depth frame

Controls:
  q  – quit
  p  – pause / resume
"""

import sys
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
MODEL_PATH = HERE / "detection" / "best.pt"

# ── stream settings ────────────────────────────────────────────────────────────
WIDTH, HEIGHT, FPS = 1280, 720, 30
DEPTH_WIDTH, DEPTH_HEIGHT = 1280, 720

# ── depth settings ────────────────────────────────────────────────────────────
# D455 minimum reliable stereo depth is ~0.4 m.
# Objects closer than this will show unreliable readings.
DEPTH_MIN_RELIABLE = 0.4   # metres (~16 in)
DEPTH_MAX_RELIABLE = 6.0   # metres (~236 in)
# Percentile used to pick the "closest surface" inside a bounding box.
# 10th percentile filters noise/holes while still returning the near surface.
DEPTH_PERCENTILE = 10

# ── colour palette for classes ─────────────────────────────────────────────────
PALETTE = [
    (0, 255, 0), (255, 100, 0), (0, 100, 255), (255, 0, 200),
    (0, 255, 200), (200, 255, 0), (100, 0, 255), (255, 200, 100),
]


def sample_depth_bbox(depth_frame: rs.depth_frame,
                      x1: int, y1: int, x2: int, y2: int,
                      w: int, h: int) -> float:
    """Return the DEPTH_PERCENTILE-th depth (m) inside the bounding box.

    Using a low percentile instead of the median gives the nearest valid
    surface in the box, which is almost always the detected object rather
    than the background behind it.
    """
    x0c = max(0, x1)
    y0c = max(0, y1)
    x1c = min(w - 1, x2)
    y1c = min(h - 1, y2)
    # Convert the bbox region to a numpy array in one call via the depth frame
    depth_data = np.asanyarray(depth_frame.get_data())   # uint16, millimetres
    roi = depth_data[y0c:y1c + 1, x0c:x1c + 1].flatten()
    valid = roi[roi > 0].astype(np.float32) / 1000.0     # mm → m
    if valid.size == 0:
        return 0.0
    return float(np.percentile(valid, DEPTH_PERCENTILE))


def annotate(frame: np.ndarray, results, depth_frame,
             model_names: dict, w: int, h: int) -> np.ndarray:
    """Draw YOLO boxes + depth labels onto *frame* (BGR, in-place copy)."""
    out = frame.copy()

    if results is None or len(results[0].boxes) == 0:
        return out

    boxes = results[0].boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = model_names.get(cls_id, str(cls_id))
        colour = PALETTE[cls_id % len(PALETTE)]

        # Depth — low-percentile across the full bbox
        depth_m = sample_depth_bbox(depth_frame, x1, y1, x2, y2, w, h) \
                  if depth_frame else 0.0
        reliable = DEPTH_MIN_RELIABLE <= depth_m <= DEPTH_MAX_RELIABLE
        depth_in = depth_m * 39.3701
        if depth_m <= 0:
            depth_str = "?\""
        elif not reliable:
            depth_str = f"{depth_in:.1f}\" (!)"
        else:
            depth_str = f"{depth_in:.1f}\""
        label_colour = (0, 0, 0) if reliable else (0, 0, 200)  # red text if unreliable

        # Box
        cv2.rectangle(out, (x1, y1), (x2, y2), colour, 2)

        # Label background
        text = f"{label} {conf:.2f} {depth_str}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        ty = max(y1 - 4, th + 4)
        cv2.rectangle(out, (x1, ty - th - 4), (x1 + tw + 4, ty + 2), colour, -1)
        cv2.putText(out, text, (x1 + 2, ty - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, label_colour, 1, cv2.LINE_AA)

        # Centre dot
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(out, (cx, cy), 3, (0, 0, 255), -1)

    return out


def add_status_bar(frame: np.ndarray, fps: float, paused: bool) -> np.ndarray:
    """Draw FPS / controls text in the bottom-left corner."""
    status = "PAUSED  " if paused else ""
    status += f"FPS: {fps:.1f}  |  [q] quit  [p] pause"
    cv2.putText(frame, status, (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 0), 1, cv2.LINE_AA)
    return frame


def main() -> None:
    # ── load model ─────────────────────────────────────────────────────────────
    if not MODEL_PATH.exists():
        sys.exit(f"[ERROR] Model not found: {MODEL_PATH}")
    print(f"[INFO] Loading YOLO model from {MODEL_PATH} …")
    model = YOLO(str(MODEL_PATH))
    model_names: dict = model.names
    print(f"[INFO] Classes: {list(model_names.values())}")

    # ── RealSense pipeline ─────────────────────────────────────────────────────
    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
    cfg.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, rs.format.z16, FPS)

    align = rs.align(rs.stream.color)   # align depth to colour frame

    print("[INFO] Starting RealSense D455 …")
    try:
        profile = pipeline.start(cfg)
    except RuntimeError as exc:
        sys.exit(f"[ERROR] Could not start RealSense pipeline: {exc}")

    # Disable IR emitter (optional — reduces pattern interference on IR images)
    depth_sensor = profile.get_device().first_depth_sensor()
    try:
        depth_sensor.set_option(rs.option.emitter_enabled, 1)
    except Exception:
        pass

    # ── state ──────────────────────────────────────────────────────────────────
    paused = False
    fps_timer = time.perf_counter()
    fps_val = 0.0
    frame_count = 0
    last_frame: Optional[np.ndarray] = None

    print("[INFO] Window open. Press  q=quit  p=pause")
    cv2.namedWindow("D455 YOLO Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("D455 YOLO Detection", WIDTH, HEIGHT)

    try:
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                paused = not paused

            if paused:
                if last_frame is not None:
                    cv2.imshow("D455 YOLO Detection",
                               add_status_bar(last_frame.copy(), fps_val, paused=True))
                continue

            # ── grab frames ───────────────────────────────────────────────────
            try:
                frameset = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                continue

            aligned = align.process(frameset)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            color_bgr = np.asanyarray(color_frame.get_data())

            # ── YOLO inference ────────────────────────────────────────────────
            results = model(
                color_bgr,
                verbose=False,
                conf=0.35,
                iou=0.45,
            )

            # ── annotate ──────────────────────────────────────────────────────
            frame_ann = annotate(color_bgr, results, depth_frame,
                                 model_names, WIDTH, HEIGHT)

            # ── FPS ───────────────────────────────────────────────────────────
            frame_count += 1
            now = time.perf_counter()
            elapsed = now - fps_timer
            if elapsed >= 1.0:
                fps_val = frame_count / elapsed
                frame_count = 0
                fps_timer = now

            # ── show UI ───────────────────────────────────────────────────────
            add_status_bar(frame_ann, fps_val, paused=False)
            cv2.imshow("D455 YOLO Detection", frame_ann)
            last_frame = frame_ann

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        print("[INFO] Pipeline stopped.")


if __name__ == "__main__":
    main()
