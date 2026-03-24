# subsystem_monitor.py
# Needs target_found from vision_module, motion_state from motion_module, gripper_state from gripper_module.
# This module becomes a collector of other subsystems' internal state.

import vision_module
import motion_module
import gripper_module


def log_robot_status():
    print("target_found from vision_module:", vision_module.target_found)
    print("motion_state from motion_module:", motion_module.motion_state)
    print("gripper_state from gripper_module:", gripper_module.gripper_state)

