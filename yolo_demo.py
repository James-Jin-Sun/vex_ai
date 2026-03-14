import argparse
import sys
import time
from pathlib import Path

try:
    import cv2
except ImportError as error:
    raise SystemExit(
        "OpenCV is not installed. Install it with: pip install opencv-python"
    ) from error

try:
    import torch
except ImportError:
    torch = None


def load_yolo_class():
    if torch is None:
        raise SystemExit(
            "PyTorch is not installed. Install a compatible torch build before running this demo."
        )

    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise SystemExit(
            "Ultralytics is not installed or could not be imported. Install it with: pip install ultralytics"
        ) from error

    return YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local webcam demo with a trained YOLO model."
    )
    parser.add_argument("--model", default="best.pt", help="Path to YOLO weights")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    parser.add_argument("--width", type=int, default=1280, help="Requested capture width")
    parser.add_argument("--height", type=int, default=720, help="Requested capture height")
    parser.add_argument("--fps", type=int, default=30, help="Requested webcam FPS")
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Inference device selection",
    )
    return parser.parse_args()


def resolve_device(requested: str) -> tuple[str, str, bool]:
    if requested == "cpu":
        return "cpu", "CPU", False

    if torch is None:
        if requested == "cuda":
            raise SystemExit(
                "PyTorch is not installed, so CUDA cannot be used. Install a CUDA-enabled PyTorch build first."
            )
        return "cpu", "CPU (torch not installed)", False

    if requested == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit(
                "CUDA was requested but is not available in this Python environment."
            )
        return "cuda:0", torch.cuda.get_device_name(0), True

    if torch.cuda.is_available():
        return "cuda:0", torch.cuda.get_device_name(0), True

    return "cpu", "CPU", False


def open_camera(camera_index: int, width: int, height: int, fps: int) -> cv2.VideoCapture:
    backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
    capture = cv2.VideoCapture(camera_index, backend)
    if not capture.isOpened():
        capture = cv2.VideoCapture(camera_index)

    if not capture.isOpened():
        raise RuntimeError(f"Could not open webcam index {camera_index}.")

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)
    return capture


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.exists():
        raise SystemExit(f"Model file not found: {model_path.resolve()}")

    yolo_class = load_yolo_class()
    device, device_label, use_half = resolve_device(args.device)
    print(f"Loading model from: {model_path.resolve()}")
    print(f"Using device: {device_label} ({device})")

    model = yolo_class(str(model_path))

    capture = open_camera(args.camera, args.width, args.height, args.fps)
    window_name = "YOLO Demo"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            success, frame = capture.read()
            if not success:
                print("Failed to read a frame from the webcam.")
                break

            results = model.predict(
                source=frame,
                imgsz=args.imgsz,
                conf=args.conf,
                iou=args.iou,
                device=device,
                half=use_half,
                verbose=False,
            )

            result = results[0]
            annotated = result.plot()

            frame_count += 1
            elapsed = max(time.time() - start_time, 1e-6)
            fps = frame_count / elapsed
            inference_ms = result.speed.get("inference", 0.0)

            cv2.putText(
                annotated,
                f"Device: {device_label}",
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                annotated,
                f"FPS: {fps:.1f} | Inference: {inference_ms:.1f} ms",
                (12, 56),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                annotated,
                "Press q to quit",
                (12, 84),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            cv2.imshow(window_name, annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()