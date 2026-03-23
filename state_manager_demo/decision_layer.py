"""
Decision Layer
==============
Responsible for decision making using state from all layers.
"""

import logging
from state_manager import StateManager

logger = logging.getLogger(__name__)


class DecisionLayer:
    """Layer for high-level decision making"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        logger.info("DecisionLayer initialized")
    
    def make_decision(self) -> str:
        """Make decision based on current state from all layers"""
        
        # Query shared state
        robot_pose = self.state_manager.get_robot_pose()
        motion_state = self.state_manager.get_motion_state()
        localized_objects = self.state_manager.get_localized_objects()
        
        # Simple decision logic
        logger.info(f"Making decision with {len(localized_objects)} localized objects")
        
        if len(localized_objects) == 0:
            decision = "SEARCH"
        elif motion_state.vx > 5.0:
            decision = "APPROACH"
        else:
            decision = "GRAB"
        
        logger.info(f"Decision: {decision}")
        return decision
