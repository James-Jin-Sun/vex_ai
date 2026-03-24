# intake_module.py
# Only talks to RobotStateManager.

def run_intake(robot_state_manager):
    robot_state_manager.update_intake_state()

