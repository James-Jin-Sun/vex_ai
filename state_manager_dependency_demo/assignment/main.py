from state_manager import RobotStateManager
import vision_module
import motion_module
import intake_module
import score_module
import peer_to_peer_communication_module
import teammate_state_module
import opponent_position_module
import game_score_module
import subsystem_monitor

print("=== ASSIGNMENT: VEX AI Robot with 9 Modules ===")
robot_state_manager = RobotStateManager()

print("\n[Running core modules...]")
vision_module.run_vision(robot_state_manager)
motion_module.run_motion(robot_state_manager)
intake_module.run_intake(robot_state_manager)

print("\n[Running scoring and game logic...]")
score_module.run_score(robot_state_manager)
game_score_module.run_game_score(robot_state_manager)

print("\n[Running communication modules...]")
peer_to_peer_communication_module.run_p2p_communication(robot_state_manager)
teammate_state_module.run_teammate_state(robot_state_manager)

print("\n[Running opponent detection...]")
opponent_position_module.run_opponent_position(robot_state_manager)

subsystem_monitor.log_robot_status(robot_state_manager)
