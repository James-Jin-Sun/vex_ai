import vision_module
import motion_module
import gripper_module
import subsystem_monitor

print("=== BAD EXAMPLE: VEX AI Robot Dependency Mess ===")
vision_module.detect_target(True)
motion_module.update_motion_state()
gripper_module.update_gripper_state()
subsystem_monitor.log_robot_status()
print("motion_module also reads gripper_state:", motion_module.coordinate_with_gripper())
