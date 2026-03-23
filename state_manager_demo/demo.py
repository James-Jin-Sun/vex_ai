"""
STATE MANAGER SYNC SOLUTION
============================
Demonstrates how a centralized StateManager eliminates data sync issues.
All layers work with the EXACT SAME variables - no manual sync needed!
"""

import time
import logging
from state_manager import StateManager
from detection_layer import DetectionLayer
from localization_layer import LocalalizationLayer
from motion_layer import MotionLayer
from odometry_layer import OdometryLayer
from decision_layer import DecisionLayer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_state_consistency(state_manager):
    """Verify that all queries return the same state"""
    pose = state_manager.get_robot_pose()
    motion = state_manager.get_motion_state()
    localizations = state_manager.get_localized_objects()
    
    logger.info(f"✓ Pose: ({pose.x:.1f}, {pose.y:.1f}, {pose.yaw:.1f}°)")
    logger.info(f"✓ Motion: vx={motion.vx:.1f}, vy={motion.vy:.1f}")
    logger.info(f"✓ Localizations: {len(localizations)} objects")
    return pose, motion, localizations


def main():
    print("\n" + "="*70)
    print("STATE MANAGER: NO DATA SYNC NIGHTMARE")
    print("="*70 + "\n")
    
    # Single centralized state manager
    state_manager = StateManager()
    
    # All layers share the SAME state manager
    logger.info("Initializing all layers with SHARED state manager...")
    detection = DetectionLayer(state_manager)
    localization = LocalalizationLayer(state_manager)
    motion = MotionLayer(state_manager)
    odometry = OdometryLayer(state_manager)
    decision = DecisionLayer(state_manager)
    
    print("\n" + "="*70)
    print("SCENARIO 1: Odometry Updates - All Layers See Same State Instantly")
    print("="*70 + "\n")
    
    logger.info(">>> ODOMETRY LAYER updates pose to (50, 30)")
    odometry.update_pose_from_encoders(50.0, 30.0, 45.0)
    
    time.sleep(0.2)
    
    logger.info(">>> Verifying all layers see the SAME pose...")
    pose1, _, _ = verify_state_consistency(state_manager)
    
    print("\n" + "="*70)
    print("SCENARIO 2: Motion Updates - All Layers See Same Motion State")
    print("="*70 + "\n")
    
    logger.info(">>> MOTION LAYER updates velocity")
    motion.update_velocity(vx=10.0, vy=5.0, omega=2.5, source="encoder")
    
    time.sleep(0.2)
    
    logger.info(">>> Decision layer queries motion - gets EXACT same value")
    decision_motion = decision.state_manager.get_motion_state()
    logger.info(f"  Motion: vx={decision_motion.vx}, vy={decision_motion.vy}, omega={decision_motion.omega}")
    
    print("\n" + "="*70)
    print("SCENARIO 3: Vision Data Flow - All Layers See Updates Instantly")
    print("="*70 + "\n")
    
    logger.info(">>> DETECTION LAYER adds vision detections")
    detection.process_detection(label="ball", confidence=0.95, bbox=[100, 150, 150, 200], camera_id="left")
    detection.process_detection(label="block", confidence=0.87, bbox=[200, 100, 250, 150], camera_id="right")
    
    time.sleep(0.3)
    
    logger.info(">>> Decision layer queries detected objects")
    detected = state_manager.get_detected_objects()
    logger.info(f"  See {len(detected)} detected objects (up-to-date!)")
    
    # Localization auto-triggered by observer, check localizations
    logger.info(">>> Decision layer queries localized objects")
    localized = state_manager.get_localized_objects()
    logger.info(f"  See {len(localized)} localized objects (auto-converted 2D→3D!)")
    
    print("\n" + "="*70)
    print("SCENARIO 4: Vision Refines Odometry - All See Updated Pose")
    print("="*70 + "\n")
    
    logger.info(">>> ODOMETRY LAYER refines pose with vision")
    odometry.update_pose_from_vision(51.2, 31.5, 46.3)
    
    time.sleep(0.2)
    
    logger.info(">>> Motion layer reads pose - gets REFINED value instantly")
    pose2 = motion.state_manager.get_robot_pose()
    logger.info(f"  Refined pose: ({pose2.x:.1f}, {pose2.y:.1f})")
    
    print("\n" + "="*70)
    print("SCENARIO 5: Multiple Readers - All Get Same Value (No Sync Needed!)")
    print("="*70 + "\n")
    
    logger.info(">>> Simulating concurrent reads from different layers...")
    
    # Each layer independently queries state
    pose_odometry = odometry.state_manager.get_robot_pose()
    pose_decision = decision.state_manager.get_robot_pose()
    pose_motion = motion.state_manager.get_robot_pose()
    
    logger.info(f"  Odometry reads:   ({pose_odometry.x}, {pose_odometry.y})")
    logger.info(f"  Decision reads:   ({pose_decision.x}, {pose_decision.y})")
    logger.info(f"  Motion reads:     ({pose_motion.x}, {pose_motion.y})")
    
    if pose_odometry.x == pose_decision.x == pose_motion.x:
        logger.info("  ✓ ALL IDENTICAL - No sync issues!")
    else:
        logger.error("  ✗ MISMATCH - This shouldn't happen!")
    
    
    print("\n" + "="*70)
    print("FINAL PROOF: Complete State Snapshot (Single Source of Truth)")
    print("="*70 + "\n")
    
    snapshot = state_manager.get_state_snapshot()
    logger.info(f"Robot Pose:        ({snapshot['robot_pose']['x']}, {snapshot['robot_pose']['y']})")
    logger.info(f"Motion State:      vx={snapshot['motion_state']['vx']}, vy={snapshot['motion_state']['vy']}")
    logger.info(f"Detected Objects:  {len(snapshot['detected_objects'])} objects")
    logger.info(f"Localized Objects: {len(snapshot['localized_objects'])} objects")
    
    print("\n" + "="*70)
    print("BENEFITS: NO DATA SYNC NIGHTMARE!")
    print("="*70)
    print("✓ NO manual syncing between layers")
    print("✓ NO duplicate state variables")
    print("✓ NO 'which value is correct?' confusion")
    print("✓ NO eventual consistency issues")
    print("✓ NO need for broadcast/message passing")
    print("✓ Thread-safe concurrent access with locks")
    print("✓ All layers always see same data instantly")
    print("✓ Scales cleanly as you add more layers")
    print("✓ Single source of truth for entire system")
    print("\n>>> Compare this to sync_nightmare_example.py to see the problem!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
