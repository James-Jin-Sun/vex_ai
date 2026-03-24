"""
STUDENT EXERCISE: Build a Multi-Layer System (The Hard Way)
=============================================================

Purpose: Experience the pain of manual syncing and lack of thread-safety,
then understand why a centralized StateManager is necessary.

Challenge Level: Intermediate

YOUR TASK:
----------
Build a system where multiple layers (Detection, Motion, Odometry, Decision)
work together WITHOUT a centralized StateManager. You must:

1. Make each layer maintain its own state copy
2. Manually sync data between layers
3. Identify and handle thread-safety issues
4. Notice the O(N²) complexity problem

WHAT WILL GO WRONG:
-------------------
✗ Layers have inconsistent state
✗ Race conditions with concurrent access
✗ Forgetting to sync = silent bugs
✗ Scalability nightmare as you add more layers
✗ Impossible to debug which layer is "correct"

THEN YOU'LL APPRECIATE: Why ../demo.py uses a centralized StateManager!

INSTRUCTIONS:
=============
1. Read the skeleton code below
2. Implement the Student TODO sections
3. Run the code and observe the problems
4. Try to fix the issues
5. Compare your solution to ../demo.py

Let's begin!
"""

import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


print(__doc__)


# ============================================================================
# PART 1: SKELETON CODE (PROVIDED)
# ============================================================================

@dataclass
class RobotPose:
    """Robot position"""
    x: float
    y: float
    yaw: float


@dataclass
class DetectedObject:
    """Vision detection"""
    label: str
    confidence: float
    x: float
    y: float


@dataclass
class MotionState:
    """Robot velocity"""
    vx: float
    vy: float
    omega: float


# ============================================================================
# PART 2: STUDENT TODO - Build Independent Layers
# ============================================================================

class StudentMotionLayer:
    """
    Motion layer that tracks robot velocity.
    
    NOTICE: It maintains its OWN copy of state - this is the problem!
    """
    
    def __init__(self):
        # ⚠️ DUPLICATE! This is its own copy of state
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0
    
    def update_velocity(self, vx: float, vy: float, omega: float):
        # Just updates its own copy (no syncing to other layers!)
        self.vx = vx
        self.vy = vy
        self.omega = omega
    
    def get_velocity(self) -> MotionState:
        # Returns its own copy (might be out of sync with other layers!)
        return MotionState(vx=self.vx, vy=self.vy, omega=self.omega)


class StudentOdometryLayer:
    """
    Odometry layer that tracks robot pose.
    
    NOTICE: It also maintains its OWN copy of state - this is also the problem!
    """
    
    def __init__(self):
        # ⚠️ DUPLICATE! This is its own copy of state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
    
    def update_pose(self, x: float, y: float, yaw: float):
        # Just updates its own copy (no syncing to other layers!)
        self.x = x
        self.y = y
        self.yaw = yaw
    
    def get_pose(self) -> RobotPose:
        # Returns its own copy (might be out of sync with Motion and Detection!)
        return RobotPose(x=self.x, y=self.y, yaw=self.yaw)


class StudentDetectionLayer:
    """
    Detection layer for vision.
    
    NOTICE: It maintains its OWN list - yet another separate copy!
    """
    
    def __init__(self):
        # ⚠️ DUPLICATE! This is its own list of detections
        self.detections = []
    
    def add_detection(self, obj: DetectedObject):
        # Just adds to its own list (no syncing!)
        self.detections.append(obj)
    
    def get_detections(self) -> List[DetectedObject]:
        # Returns its own list
        return self.detections.copy()
    
    def clear_detections(self):
        # Clears only its own list
        self.detections.clear()


class StudentDecisionLayer:
    """
    Decision layer that queries other layers.
    
    PROBLEM: Must manually query each layer for current state!
    """
    
    def __init__(self, motion_layer, odometry_layer, detection_layer):
        self.motion_layer = motion_layer
        self.odometry_layer = odometry_layer
        self.detection_layer = detection_layer
    
    def make_decision(self) -> str:
        # Must manually query each layer (they might be out of sync!)
        motion = self.motion_layer.get_velocity()
        pose = self.odometry_layer.get_pose()
        detections = self.detection_layer.get_detections()
        
        if len(detections) == 0:
            return "SEARCH"
        elif motion.vx > 5.0:
            return "APPROACH"
        else:
            return "GRAB"


# ============================================================================
# PART 3: MANUAL SYNCING - THE NIGHTMARE!
# ============================================================================

class StudentSyncCoordinator:
    """
    Manual syncing between layers - THIS IS THE NIGHTMARE!
    
    Challenge: When odometry updates, motion needs to know about it!
    """
    
    def __init__(self, motion_layer, odometry_layer, detection_layer):
        self.motion_layer = motion_layer
        self.odometry_layer = odometry_layer
        self.detection_layer = detection_layer
    
    def sync_odometry_to_motion(self, pose: RobotPose):
        """
        Manually update motion's internal state when odometry changes.
        ⚠️ This is awkward! Motion doesn't expose state setters!
        We have to update its private attributes!
        """
        # HACK: Directly modify private attributes (bad practice!)
        self.motion_layer.x = pose.x
        self.motion_layer.y = pose.y
        self.motion_layer.yaw = pose.yaw
        print(f"  [SYNC] Odometry → Motion: ({pose.x}, {pose.y})")
    
    def sync_motion_to_decision(self):
        """Prepare motion data for decision layer"""
        motion = self.motion_layer.get_velocity()
        print(f"  [SYNC] Motion → Decision: vx={motion.vx}, vy={motion.vy}")
    
    def sync_detection_to_decision(self):
        """Prepare detection data for decision layer"""
        detections = self.detection_layer.get_detections()
        print(f"  [SYNC] Detection → Decision: {len(detections)} objects")


# ============================================================================
# PART 4: THREADING ISSUES - Race Conditions
# ============================================================================

class StudentThreadingExercise:
    """
    Experience race conditions with concurrent access.
    
    Build a scenario where multiple threads update different layers simultaneously:
    - Thread 1: Odometry updates pose
    - Thread 2: Motion updates velocity
    - Thread 3: Detection adds objects
    - Thread 4: Decision reads all state
    
    Problem: Without locks, Thread 4 might see:
    - Half-updated odometry data
    - Half-updated motion data
    - Inconsistent state = BUGS!
    
    Notice: You need N locks for N layers, and must coordinate them!
    (StateManager solves this with ONE lock for all state!)
    """
    
    def __init__(self, motion_layer, odometry_layer, detection_layer, decision_layer):
        self.motion_layer = motion_layer
        self.odometry_layer = odometry_layer
        self.detection_layer = detection_layer
        self.decision_layer = decision_layer
        self.race_condition_detected = False
        self.results = []
    
    def thread_odometry_updates(self):
        """Thread 1: Continuously update odometry"""
        for i in range(5):
            self.odometry_layer.update_pose(50.0 + i, 30.0 + i, 45.0 + i)
            print(f"    [T1-Odometry] Update {i}: pose updated")
            time.sleep(0.005)
    
    def thread_motion_updates(self):
        """Thread 2: Continuously update motion"""
        for i in range(5):
            self.motion_layer.update_velocity(10.0 + i, 5.0 - i*0.5, 2.5 + i)
            print(f"    [T2-Motion] Update {i}: velocity updated")
            time.sleep(0.006)
    
    def thread_detection_updates(self):
        """Thread 3: Continuously add detections"""
        for i in range(5):
            det = DetectedObject(label=f"obj_{i}", confidence=0.9 + i*0.01, x=100+i*10, y=150+i*5)
            self.detection_layer.add_detection(det)
            print(f"    [T3-Detection] Update {i}: object added")
            time.sleep(0.007)
    
    def thread_decision_reads(self):
        """Thread 4: Continuously read all state"""
        for i in range(5):
            try:
                # Try to read all state at once - RACE CONDITION HERE!
                motion = self.motion_layer.get_velocity()
                pose = self.odometry_layer.get_pose()
                detections = self.detection_layer.get_detections()
                
                state_snapshot = {
                    'iteration': i,
                    'vx': motion.vx,
                    'pose_x': pose.x,
                    'detections_count': len(detections)
                }
                self.results.append(state_snapshot)
                print(f"    [T4-Decision] Read {i}: vx={motion.vx:.1f}, x={pose.x:.1f}, dets={len(detections)}")
                
                # Check for inconsistency
                if i > 0 and i < 4:
                    prev = self.results[i-1]
                    # If values don't match expected progression, race condition!
                    if abs(state_snapshot['vx'] - prev['vx']) > 2.0:
                        self.race_condition_detected = True
                        print(f"    ⚠️ RACE CONDITION: vx jumped from {prev['vx']} to {state_snapshot['vx']}")
            
            except Exception as e:
                print(f"    ❌ [T4-Decision] ERROR reading state: {e}")
                self.race_condition_detected = True
            
            time.sleep(0.008)
    
    def run_concurrent_test(self):
        """Run all 4 threads concurrently and observe chaos!"""
        print("\n" + "="*70)
        print("THREADING TEST: 4 Concurrent Threads Without Synchronization")
        print("="*70)
        print("Watch for inconsistent state reads and race conditions!\n")
        
        self.race_condition_detected = False
        self.results = []
        
        # Start all 4 threads
        t1 = threading.Thread(target=self.thread_odometry_updates, daemon=True)
        t2 = threading.Thread(target=self.thread_motion_updates, daemon=True)
        t3 = threading.Thread(target=self.thread_detection_updates, daemon=True)
        t4 = threading.Thread(target=self.thread_decision_reads, daemon=True)
        
        print("Starting threads...\n")
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        
        # Wait for all to complete
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        
        print("\n" + "-"*70)
        print("RESULTS:")
        if self.race_condition_detected:
            print("❌ RACE CONDITION DETECTED!")
            print("Multiple threads saw inconsistent state during concurrent access.")
        else:
            print("⚠️ All reads completed, but timing issues might still exist.")
        print(f"Captured {len(self.results)} state snapshots")
        print("-"*70 + "\n")


# ============================================================================
# PART 5: TEST SUITE
# ============================================================================

def run_tests():
    """
    Demonstrate the problems with distributed state across layers.
    
    Tests show why manual syncing fails and why a centralized StateManager is necessary.
    """
    
    print("\n" + "="*70)
    print("COMPREHENSIVE TESTS: Problems Without Centralized State")
    print("="*70 + "\n")
    
    # Test 1: State Inconsistency
    print("TEST 1: State Inconsistency")
    print("-" * 70)
    motion1 = StudentMotionLayer()
    odometry1 = StudentOdometryLayer()
    
    odometry1.update_pose(100.0, 50.0, 90.0)
    motion1.update_velocity(15.0, 8.0, 3.0)
    
    # Now query both layers
    motion_state = motion1.get_velocity()
    odometry_state = odometry1.get_pose()
    
    print(f"Odometry: x={odometry_state.x}, y={odometry_state.y}, yaw={odometry_state.yaw}")
    print(f"Motion: vx={motion_state.vx}, vy={motion_state.vy}, omega={motion_state.omega}")
    print("❌ PROBLEM: Motion layer doesn't know odometry was updated!")
    print("   They maintain SEPARATE copies of state!\n")
    
    # Test 2: Missing Sync Bug
    print("TEST 2: The Forgotten Sync Problem")
    print("-" * 70)
    motion2 = StudentMotionLayer()
    odometry2 = StudentOdometryLayer()
    detection2 = StudentDetectionLayer()
    decision2 = StudentDecisionLayer(motion2, odometry2, detection2)
    
    # Simulate: odometry updates but sync is FORGOT
    odometry2.update_pose(50.0, 30.0, 45.0)
    motion2.update_velocity(10.0, 5.0, 2.5)
    # ❌ FORGOT TO CALL sync function!
    
    # Add detection and check decision
    det = DetectedObject(label="ball", confidence=0.95, x=100, y=150)
    detection2.add_detection(det)
    
    decision_result = decision2.make_decision()
    print(f"Decision made: {decision_result}")
    print("❌ PROBLEM: Forgot to sync! Decision is based on INCOMPLETE state!")
    print("   (Silent bug - code runs but uses old data)\n")
    
    # Test 3: Scalability Nightmare
    print("TEST 3: Scalability Nightmare (N-layer complexity)")
    print("-" * 70)
    
    n_layers = 5
    n_connections = n_layers * (n_layers - 1) // 2
    print(f"With {n_layers} layers, you need {n_connections} sync relationships:")
    print("Formula: N layers = N×(N-1)/2 connections")
    
    scenarios = [
        (3, 3),
        (4, 6),
        (5, 10),
        (6, 15),
        (10, 45),
        (20, 190),
    ]
    
    for layers, syncs in scenarios:
        print(f"  • {layers:2d} layers → {syncs:3d} sync relationships (O(N²) complexity!)")
    
    print("❌ NIGHTMARE: Each sync relationship is code you must write and maintain!")
    print("             Each sync call you might forget!")
    print("             Each sync relationship is a potential race condition!\n")
    
    # Test 4: Threading Race Condition
    print("TEST 4: Threading Race Conditions")
    print("-" * 70)
    motion4 = StudentMotionLayer()
    odometry4 = StudentOdometryLayer()
    detection4 = StudentDetectionLayer()
    decision4 = StudentDecisionLayer(motion4, odometry4, detection4)
    
    exercise = StudentThreadingExercise(motion4, odometry4, detection4, decision4)
    exercise.run_concurrent_test()
    
    # Test 5: Missing Data Type Consistency
    print("TEST 5: Type Mismatches and Confusion")
    print("-" * 70)
    print("Each layer maintains a DIFFERENT structure:")
    print("  • StudentMotionLayer: vx, vy, omega (floats)")
    print("  • StudentOdometryLayer: x, y, yaw (floats)")
    print("  • StudentDetectionLayer: list of DetectedObject")
    print("❌ PROBLEM: No central schema! Easy to make mistakes!")
    print("            Hard to reason about what's \"the truth\"\n")


# ============================================================================
# PART 6: REFLECTION QUESTIONS
# ============================================================================

REFLECTION_QUESTIONS = """
After implementing this exercise, answer these questions:

1. How many separate state variables did you need to maintain?
   (Hint: Each layer has x, y, yaw, vx, vy, omega, detections, etc.)

2. How many different sync functions did you write?
   (Each connection between layers needs coordination!)

3. Did you run into race conditions with threading?
   (Multiple threads accessing unsynchronized state = CHAOS)

4. How would you add a 6th layer?
   (Need to update sync code in 5+ places!)

5. What happens if you forget to call a sync function?
   (Silent bugs! Layers think they're synced but they're not!)

6. How do you know when all layers are "consistent"?
   (In your current design: You don't! There's no guarantee!)

THEN COMPARE TO: ../demo.py where StateManager solves ALL these issues!

In demo.py:
✓ ONE copy of state (not N copies)
✓ ZERO manual sync functions (automatic!)
✓ ONE lock for thread-safety (not N locks)
✓ Adding new layers = NO changes to existing code!
✓ Impossible to forget sync (it's automatic!)
✓ Layers are ALWAYS consistent (same source of truth!)

LESSON: Centralized state + thread-safe access = architecture wins!
"""

print(REFLECTION_QUESTIONS)


# ============================================================================
# PART 7: YOUR MAIN CODE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("STUDENT EXERCISE: THE HARD WAY (Without Centralized State)")
    print("="*70 + "\n")
    
    # 1. Instantiate all 4 layers
    print(">>> Initializing layers (each with their OWN state copy)...\n")
    motion = StudentMotionLayer()
    odometry = StudentOdometryLayer()
    detection = StudentDetectionLayer()
    decision = StudentDecisionLayer(motion, odometry, detection)
    
    # 2. Try to make them work together
    print(">>> DEMO: Updating all layers with some state\n")
    
    print(">>> Updating odometry to (50, 30, 45)")
    odometry.update_pose(50.0, 30.0, 45.0)
    
    print(">>> Updating motion to (10, 5, 2.5)")
    motion.update_velocity(10.0, 5.0, 2.5)
    
    print(">>> Adding detection")
    det = DetectedObject(label="ball", confidence=0.95, x=100, y=150)
    detection.add_detection(det)
    
    print("\n>>> Making decision...")
    decision_result = decision.make_decision()
    print(f"Decision: {decision_result}\n")
    
    # 3. Run comprehensive tests demonstrating the problems
    print(">>> Running comprehensive tests...\n")
    run_tests()
    
    # 4. Summary
    print("\n" + "="*70)
    print("SUMMARY: What You've Experienced")
    print("="*70)
    print("""
YOUR SYSTEM (Distributed State):
  ✗ Each layer maintains its own data copy
  ✗ Manual syncing required between layers
  ✗ Easy to forget to sync (silent bugs!)
  ✗ Race conditions with threads
  ✗ O(N²) complexity as layers grow
  ✗ Hard to reason about "source of truth"
  ✗ Testing is complex and fragile
  ✗ Scale to 10+ layers = NIGHTMARE

DEMO.PY SYSTEM (Centralized StateManager):
  ✓ ONE copy of all state (single source of truth)
  ✓ ZERO manual syncing (automatic!)
  ✓ ONE lock for thread-safety (not N locks)
  ✓ Adding layers = NO changes to existing code!
  ✓ O(N) complexity (scales easily)
  ✓ Always consistent
  ✓ Easy to test and debug
  ✓ Scales to hundreds of layers effortlessly

LESSON: Architecture matters! Centralized state patterns solve distributed systems problems!
""")
    print("="*70)
    print("\nNOW RUN: python demo.py")
    print("And observe the elegance of the centralized StateManager solution!")
    print("="*70 + "\n")
