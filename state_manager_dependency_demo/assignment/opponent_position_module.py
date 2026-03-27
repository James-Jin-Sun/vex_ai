# opponent_position_module.py
# Gets opponent position by analyzing vision_module data.
# Depends on vision_module (indirectly through RobotStateManager).

import vision_module

def run_opponent_position(robot_state_manager):
    # First, run vision to detect targets
    vision_module.run_vision(robot_state_manager)
    
    # If target found, estimate opponent position
    if robot_state_manager.target_found:
        opponent_pos = (120, 80)  # Simulated opponent position from vision analysis
        robot_state_manager.set_opponent_position(opponent_pos)
        print(f"  [opponent_position_module] Opponent detected at: {opponent_pos}")
    else:
        print("  [opponent_position_module] No opponent visible")
