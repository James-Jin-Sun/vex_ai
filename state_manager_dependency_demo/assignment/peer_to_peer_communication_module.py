# peer_to_peer_communication_module.py
# Communicates with allied robot to share information.
# Only talks to RobotStateManager.

def run_p2p_communication(robot_state_manager):
    # Simulate sending our position to allied robot and receiving theirs
    our_position = (50, 30)  # Simulated position
    
    # In real scenario, this would communicate over network
    # For now, simulate receiving ally position
    ally_position = (75, 45)
    
    robot_state_manager.set_ally_position(ally_position)
    print(f"  [peer_to_peer_communication_module] Ally position received: {ally_position}")
