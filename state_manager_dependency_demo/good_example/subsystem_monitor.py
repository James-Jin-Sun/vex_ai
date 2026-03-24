# subsystem_monitor.py
# Reads all robot state from RobotStateManager instead of importing 3 separate modules.

def log_robot_status(robot_state_manager):
    print("target_found:", robot_state_manager.target_found)
    print("motion_state:", robot_state_manager.motion_state)
    print("gripper_state:", robot_state_manager.gripper_state)

