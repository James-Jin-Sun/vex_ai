# robot_state_manager.py
# One place for all VEX AI robot shared state.

class RobotStateManager:
    def __init__(self):
        self.target_found = False
        self.motion_state = "idle"
        self.gripper_state = "open"

    def detect_target(self, is_visible):
        self.target_found = is_visible

    def update_motion_state(self):
        if self.target_found:
            self.motion_state = "chasing"
        else:
            self.motion_state = "searching"

    def update_gripper_state(self):
        if self.target_found and self.motion_state == "chasing":
            self.gripper_state = "closing"
        else:
            self.gripper_state = "open"

