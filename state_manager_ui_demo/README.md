# State Manager UI Demo (Laptop)

Simplified OpenCV demo inspired by the VEX state-manager UI.

## What it uses
- Laptop camera (`cv2.VideoCapture(0)`)
- Fake telemetry for:
  - VEX Brain command state
  - Jetson/Nano decision and perception summary
  - Robot pose/motion/action data

## Run
From `vex_ai/state manager_ui_demo`:

```bash
python run_demo.py
```

## Controls
- `q` or `Esc`: quit
- `p`: pause/resume fake telemetry updates

## Notes
- If the camera fails to open, close other apps that are using webcam.
- You can switch camera index in code (`VideoCapture(0)` -> `VideoCapture(1)`).
