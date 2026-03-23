"""
Localization Layer (Odometry)
=============================
Responsible for updating robot pose via odometry or vision.
"""

import logging
from state_manager import StateManager

logger = logging.getLogger(__name__)


class OdometryLayer:
    """Layer for updating robot pose"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        logger.info("OdometryLayer initialized")
    
    def update_pose_from_encoders(self, x: float, y: float, yaw: float):
        """Update robot pose from encoder data"""
        self.state_manager.update_robot_pose(x, y, yaw, source="encoders")
    
    def update_pose_from_vision(self, x: float, y: float, yaw: float):
        """Update robot pose from vision-based localization"""
        self.state_manager.update_robot_pose(x, y, yaw, source="vision")
    
    def get_robot_pose(self):
        """Query current robot pose"""
        return self.state_manager.get_robot_pose()
