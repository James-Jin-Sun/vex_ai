"""
Motion Layer
============
Responsible for tracking and updating robot motion state.
"""

import logging
from state_manager import StateManager

logger = logging.getLogger(__name__)


class MotionLayer:
    """Layer for tracking robot motion"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        logger.info("MotionLayer initialized")
    
    def update_velocity(self, vx: float, vy: float, omega: float, source: str = "encoder"):
        """Update robot velocity from encoders or IMU"""
        self.state_manager.update_motion_state(vx, vy, omega, source=source)
    
    def get_motion_state(self):
        """Query current motion state"""
        return self.state_manager.get_motion_state()
