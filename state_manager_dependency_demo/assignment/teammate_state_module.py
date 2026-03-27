# teammate_state_module.py
# Calls peer_to_peer_communication_module to get and coordinate teammate robot state.
# Depends on peer_to_peer_communication_module.

import peer_to_peer_communication_module

def run_teammate_state(robot_state_manager):
    # First, get ally position via P2P communication
    peer_to_peer_communication_module.run_p2p_communication(robot_state_manager)
    
    # Now use the ally position for coordination
    ally_pos = robot_state_manager.get_ally_position()
    if ally_pos:
        print(f"  [teammate_state_module] Coordinating with teammate at {ally_pos}")
