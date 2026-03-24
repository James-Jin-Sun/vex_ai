# gripper_module.py
# Only talks to RobotStateManager.

def run_gripper(robot_state_manager):
    robot_state_manager.update_gripper_state()

