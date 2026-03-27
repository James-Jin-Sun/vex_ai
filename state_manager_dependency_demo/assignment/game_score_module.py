# game_score_module.py
# Updates the game score after successful scoring events.
# Depends on score_module to know when points were scored.

import score_module

def run_game_score(robot_state_manager):
    # Run scoring logic first
    score_module.run_score(robot_state_manager)
    
    # Update the overall game score
    robot_state_manager.update_game_score(robot_state_manager.score)
    print(f"  [game_score_module] Game score updated to: {robot_state_manager.game_score}")
