# score_module.py
# Scores points when intake successfully grabs a goal.
# Only talks to RobotStateManager.

def run_score(robot_state_manager):
    # Check if intake just closed (grabbed something)
    if robot_state_manager.intake_state == "closing":
        # Award points for successful capture
        robot_state_manager.score_points(5)
        print("  [score_module] Scored 5 points! Current score:", robot_state_manager.score)
