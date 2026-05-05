"""
Simplified State Manager UI Demo (Laptop Only)

Features:
- Uses built-in webcam (OpenCV VideoCapture(0))
- Generates fake VEX Brain / Jetson / Robot state data
- Renders a simplified dashboard panel next to camera feed

Controls:
- q or Esc: quit
- p: pause/resume fake data updates
"""

import math
import random
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass
class FakeRobotState:
    x: float
    y: float
    heading_deg: float
    speed_ips: float
    omega_dps: float
    balls: int
    action: str
    is_busy: bool
    alliance: str


@dataclass
class FakeBrainState:
    connected: bool
    brain_echo: str
    cmd_ok: Optional[bool]
    wire_cmd: str
    last_cmd_age_s: float


@dataclass
class FakeJetsonState:
    fps: float
    detections: int
    fused: int
    decision: str
    confidence: float
    processing_ms: float


class FakeStateManager:
    """Produces synthetic, time-varying telemetry for UI demonstration."""

    ACTIONS = ["IDLE", "SCOUT", "COLLECT", "GOAL", "AVOID", "ALIGN"]
    DECISIONS = ["TC", "TURN", "HOLD", "REPLAN"]

    def __init__(self) -> None:
        self.start_t = time.time()
        self.last_t = self.start_t
        self.paused = False

        self.robot = FakeRobotState(
            x=0.0,
            y=0.0,
            heading_deg=0.0,
            speed_ips=0.0,
            omega_dps=0.0,
            balls=0,
            action="IDLE",
            is_busy=False,
            alliance="blue",
        )
        self.brain = FakeBrainState(
            connected=True,
            brain_echo="idle",
            cmd_ok=None,
            wire_cmd="",
            last_cmd_age_s=99.0,
        )
        self.jetson = FakeJetsonState(
            fps=0.0,
            detections=0,
            fused=0,
            decision="none",
            confidence=0.0,
            processing_ms=0.0,
        )

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def update(self, measured_fps: float) -> None:
        now = time.time()
        dt = max(now - self.last_t, 1e-3)
        self.last_t = now

        self.jetson.fps = measured_fps

        if self.paused:
            return

        t = now - self.start_t

        # Robot motion in a smooth Lissajous-like path.
        self.robot.x = 36.0 * math.sin(t * 0.35)
        self.robot.y = 24.0 * math.cos(t * 0.27)
        self.robot.heading_deg = (t * 35.0) % 360.0
        self.robot.speed_ips = 8.0 + 10.0 * abs(math.sin(t * 0.8))
        self.robot.omega_dps = 30.0 * math.sin(t * 0.5)
        self.robot.balls = int((math.sin(t * 0.6) + 1.0) * 1.5)
        self.robot.action = random.choice(self.ACTIONS) if random.random() < 0.08 else self.robot.action
        self.robot.is_busy = self.robot.action not in ("IDLE", "HOLD")

        # Brain command state.
        if random.random() < 0.12:
            self.brain.brain_echo = random.choice(["drive", "turn", "collect", "idle"]) 
            self.brain.cmd_ok = random.choice([True, False, None])
            cmd = random.choice(self.DECISIONS)
            tx = random.uniform(-60, 60)
            ty = random.uniform(-60, 60)
            self.brain.wire_cmd = f"{cmd} {tx:.1f} {ty:.1f}" if cmd == "TC" else cmd
            self.brain.last_cmd_age_s = 0.0
        else:
            self.brain.last_cmd_age_s = min(self.brain.last_cmd_age_s + dt, 999.0)

        if random.random() < 0.01:
            self.brain.connected = not self.brain.connected

        # Jetson decision and perception summaries.
        self.jetson.detections = random.randint(0, 8)
        self.jetson.fused = random.randint(0, min(4, self.jetson.detections))
        self.jetson.decision = random.choice(["go_collect", "defend", "hold", "score", "search"])
        self.jetson.confidence = random.uniform(0.55, 0.98)
        self.jetson.processing_ms = random.uniform(8.0, 36.0)


def draw_camera_overlay(frame: np.ndarray, state: FakeStateManager) -> np.ndarray:
    out = frame.copy()

    cv2.putText(out, f"FPS: {state.jetson.fps:.1f}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(
        out,
        f"Robot ({state.robot.x:.1f}, {state.robot.y:.1f}) hdg {state.robot.heading_deg:.1f}",
        (12, 56),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        out,
        f"Detections: {state.jetson.detections} | Fused: {state.jetson.fused}",
        (12, 84),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 0),
        2,
    )

    return out


def draw_side_panel(height: int, state: FakeStateManager) -> np.ndarray:
    panel_w = 360
    panel = np.zeros((height, panel_w, 3), dtype=np.uint8)
    panel[:] = (28, 28, 28)

    WHITE = (245, 245, 245)
    GREY = (145, 145, 145)
    CYAN = (255, 255, 0)
    GREEN = (0, 220, 0)
    YELLOW = (0, 220, 255)
    RED = (60, 60, 255)
    ORANGE = (0, 165, 255)

    y = 24
    lh = 21

    def put(text: str, color=WHITE, scale=0.5, thick=1) -> None:
        nonlocal y
        cv2.putText(panel, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick)
        y += lh

    def line() -> None:
        nonlocal y
        cv2.line(panel, (8, y), (panel_w - 8, y), GREY, 1)
        y += 10

    put("STATE MANAGER UI DEMO", CYAN, 0.58, 2)
    put("Laptop mode: webcam + fake telemetry", GREY, 0.45, 1)
    line()

    put("COMMAND STATUS", CYAN, 0.55, 2)
    status_color = GREEN if state.brain.cmd_ok is True else (RED if state.brain.cmd_ok is False else GREY)
    put(f"Connected: {'YES' if state.brain.connected else 'NO'}", GREEN if state.brain.connected else RED)
    put(f"Echo: {state.brain.brain_echo}", WHITE)
    put(f"Wire: {state.brain.wire_cmd or 'none'}", status_color)
    put(f"Cmd age: {state.brain.last_cmd_age_s:.1f}s", ORANGE if state.brain.last_cmd_age_s > 5 else GREY)
    line()

    put("ROBOT STATE", CYAN, 0.55, 2)
    put(f"Alliance: {state.robot.alliance.upper()}", YELLOW)
    put(f"Pos: ({state.robot.x:.1f}, {state.robot.y:.1f}) in")
    put(f"Heading: {state.robot.heading_deg:.1f} deg")
    put(f"Speed: {state.robot.speed_ips:.1f} in/s")
    put(f"Omega: {state.robot.omega_dps:.1f} deg/s")
    put(f"Balls: {state.robot.balls}", GREEN if state.robot.balls > 0 else WHITE)
    busy_color = ORANGE if state.robot.is_busy else GREEN
    put(f"Action: {state.robot.action}", busy_color)
    put(f"Mode: {'BUSY' if state.robot.is_busy else 'IDLE'}", busy_color)
    line()

    put("JETSON SUMMARY", CYAN, 0.55, 2)
    put(f"Decision: {state.jetson.decision}")
    put(f"Confidence: {state.jetson.confidence:.0%}")
    put(f"Detections: {state.jetson.detections}  Fused: {state.jetson.fused}")
    put(f"Proc time: {state.jetson.processing_ms:.1f} ms")
    line()

    put("Controls", CYAN, 0.55, 2)
    put("q / Esc: Quit", GREY)
    put("p: Pause fake data", GREY)

    # Motion intensity bar from speed+omega (demo metric).
    intensity = min(1.0, (state.robot.speed_ips + abs(state.robot.omega_dps) * 0.4) / 30.0)
    bx0, bx1 = 10, panel_w - 10
    by = height - 24
    cv2.rectangle(panel, (bx0, by - 8), (bx1, by), (45, 45, 45), -1)
    fill = int((bx1 - bx0) * intensity)
    bcol = (0, 200, 60) if intensity < 0.4 else ((0, 180, 220) if intensity < 0.75 else (0, 60, 220))
    if fill > 0:
        cv2.rectangle(panel, (bx0, by - 8), (bx0 + fill, by), bcol, -1)
    cv2.putText(panel, "Motion intensity", (bx0, by - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, GREY, 1)

    return panel


def main() -> int:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open laptop camera (index 0).")
        print("Try closing other apps using camera or changing camera index in code.")
        return 1

    window_name = "State Manager UI Demo"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    fake = FakeStateManager()
    last_t = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[WARN] Camera frame read failed.")
                break

            now = time.time()
            fps = 1.0 / max(now - last_t, 1e-6)
            last_t = now

            fake.update(fps)

            view = draw_camera_overlay(frame, fake)
            panel = draw_side_panel(view.shape[0], fake)
            combined = np.hstack((view, panel))

            cv2.imshow(window_name, combined)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("p"):
                fake.toggle_pause()
                print(f"[INFO] {'Paused' if fake.paused else 'Resumed'} fake updates")

    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
