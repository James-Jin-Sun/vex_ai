# Needs target_found from vision_module and motion_state from motion_module.
# Also manages gripper_state.
# This creates a circular dependency because motion_module imports gripper_module too.

import vision_module
import motion_module

gripper_state = "open"

def update_gripper_state():
    global gripper_state
    if vision_module.target_found and motion_module.motion_state == "chasing":
        gripper_state = "closing"
    else:
        gripper_state = "open"

