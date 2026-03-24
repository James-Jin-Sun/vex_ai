import vision_module
import motion_module
import intake_module
import subsystem_monitor

print("=== BAD EXAMPLE: VEX AI Robot Dependency Mess ===")
vision_module.detect_target(True)
motion_module.update_motion_state()
intake_module.update_intake_state()
subsystem_monitor.log_robot_status()
print("motion_module also reads intake_state:", motion_module.coordinate_with_intake())
