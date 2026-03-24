from state_manager import RobotStateManager
import vision_module
import motion_module
import intake_module
import subsystem_monitor

print("=== GOOD EXAMPLE: VEX AI Robot with StateManager ===")
robot_state_manager = RobotStateManager()

vision_module.run_vision(robot_state_manager)
motion_module.run_motion(robot_state_manager)
intake_module.run_intake(robot_state_manager)
subsystem_monitor.log_robot_status(robot_state_manager)
