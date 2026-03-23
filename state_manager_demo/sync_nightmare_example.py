"""
DATA SYNC NIGHTMARE (Without Centralized State Manager)
=======================================================

This example shows what happens when each layer maintains its own copy of state.
Result: Data gets out of sync, modules make decisions based on stale data.
"""

import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProblematicOdometryLayer:
    """Each layer manages its OWN state - PROBLEM!"""
    
    def __init__(self):
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        logger.info("OdometryLayer initialized (has its own state copy)")
    
    def update_pose(self, x, y, yaw):
        self.robot_x = x
        self.robot_y = y
        self.robot_yaw = yaw
        logger.info(f"OdometryLayer updated: ({x}, {y}, {yaw}°)")


class ProblematicMotionLayer:
    """Each layer manages its OWN state - PROBLEM!"""
    
    def __init__(self):
        self.robot_x = 0.0  # 🚨 REDUNDANT! Should share with OdometryLayer
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        logger.info("MotionLayer initialized (has its own state copy)")
    
    def simulate_motion(self, dx, dy, dyaw):
        self.robot_x += dx
        self.robot_y += dy
        self.robot_yaw += dyaw
        logger.info(f"MotionLayer updated: ({self.robot_x}, {self.robot_y}, {self.robot_yaw}°)")


class ProblematicLocalizationLayer:
    """Each layer manages its OWN state - PROBLEM!"""
    
    def __init__(self):
        self.robot_x = 0.0  # 🚨 REDUNDANT! Should share with other layers
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        logger.info("LocalizationLayer initialized (has its own state copy)")
    
    def refine_pose(self, x, y, yaw):
        self.robot_x = x
        self.robot_y = y
        self.robot_yaw = yaw
        logger.info(f"LocalizationLayer updated: ({x}, {y}, {yaw}°)")


class ProblematicDecisionLayer:
    """Queries robot state - but from WHERE? Different layers have different values!"""
    
    def __init__(self, odometry, motion, localization):
        self.odometry = odometry
        self.motion = motion
        self.localization = localization
        logger.info("DecisionLayer initialized (queries other layers)")
    
    def make_decision(self):
        logger.info("DecisionLayer attempting to read robot state...")
        
        # 🚨 PROBLEM: Each layer has different values!
        logger.warning(f"  Odometry sees: ({self.odometry.robot_x}, {self.odometry.robot_y})")
        logger.warning(f"  Motion sees:   ({self.motion.robot_x}, {self.motion.robot_y})")
        logger.warning(f"  Localization sees: ({self.localization.robot_x}, {self.localization.robot_y})")
        
        # Which one is correct? 🤔
        if self.odometry.robot_x != self.motion.robot_x:
            logger.error("❌ STATE MISMATCH! Different layers have different robot positions!")
        
        return "CONFUSED"


def main():
    print("\n" + "="*70)
    print("DATA SYNC NIGHTMARE DEMO (Without StateManager)")
    print("="*70 + "\n")
    
    # Initialize each layer with its own state
    odometry = ProblematicOdometryLayer()
    motion = ProblematicMotionLayer()
    localization = ProblematicLocalizationLayer()
    decision = ProblematicDecisionLayer(odometry, motion, localization)
    
    print("\n" + "="*70)
    print("SCENARIO: Multiple Layers Update State Independently")
    print("="*70 + "\n")
    
    logger.info(">>> Odometry updates pose to (50, 30)")
    odometry.update_pose(50.0, 30.0, 45.0)
    
    time.sleep(0.5)
    
    logger.info(">>> Motion simulates movement (+5, +3)")
    motion.simulate_motion(5.0, 3.0, 5.0)
    
    time.sleep(0.5)
    
    logger.info(">>> Localization refines pose with vision data")
    localization.refine_pose(51.2, 31.5, 46.3)
    
    time.sleep(0.5)
    
    print("\n" + "="*70)
    print("Decision Layer Queries State - But Gets Conflicting Data!")
    print("="*70 + "\n")
    
    decision.make_decision()
    
    print("\n" + "="*70)
    print("THE NIGHTMARE:")
    print("="*70)
    print(f"Odometry Layer state:      ({odometry.robot_x}, {odometry.robot_y})")
    print(f"Motion Layer state:        ({motion.robot_x}, {motion.robot_y})")
    print(f"Localization Layer state:  ({localization.robot_x}, {localization.robot_y})")
    print("\n❌ Three different positions! Which is the truth?")
    print("❌ Each layer is 'correct' from its own perspective")
    print("❌ Decision layer doesn't know which to trust")
    print("❌ Manual sync/reconciliation code needed everywhere")
    print("❌ Scalability nightmare as you add more layers")
    print("\nSOLUTION: All layers share the EXACT SAME state via StateManager!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
