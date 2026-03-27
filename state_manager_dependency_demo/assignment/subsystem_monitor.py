# subsystem_monitor.py
# Logs all robot state from RobotStateManager.

def log_robot_status(robot_state_manager):
    print("\n" + "="*60)
    print("ROBOT STATUS")
    print("="*60)
    print("target_found:", robot_state_manager.target_found)
    print("motion_state:", robot_state_manager.motion_state)
    print("intake_state:", robot_state_manager.intake_state)
    print("score:", robot_state_manager.score)
    print("ally_robot_position:", robot_state_manager.ally_robot_position)
    print("opponent_position:", robot_state_manager.opponent_position)
    print("game_score:", robot_state_manager.game_score)
    print("="*60 + "\n")

