from state_manager import RobotStateManager
import vision_module
import motion_module
import gripper_module
import subsystem_monitor

print("=== GOOD EXAMPLE: VEX AI Robot with StateManager ===")
robot_state_manager = RobotStateManager()

vision_module.run_vision(robot_state_manager)
motion_module.run_motion(robot_state_manager)
gripper_module.run_gripper(robot_state_manager)
subsystem_monitor.log_robot_status(robot_state_manager)
