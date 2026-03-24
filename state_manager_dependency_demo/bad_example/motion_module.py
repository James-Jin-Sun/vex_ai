# Needs target_found from vision_module, and updates motion_state based on it.
import vision_module

motion_state = "idle"

def update_motion_state():
    global motion_state
    if vision_module.target_found:
        motion_state = "chasing"
    else:
        motion_state = "searching"

import gripper_module

def coordinate_with_gripper():
    # motion_module now also depends on gripper_module.gripper_state
    return gripper_module.gripper_state

