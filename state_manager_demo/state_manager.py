"""
Simplified State Manager
========================
Centralized state management with thread-safe CRUD operations.
Single source of truth for all system state.
"""

import threading
import time
import copy
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemStatus(Enum):
    """System operational status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class RobotPose:
    """Robot pose in world coordinates"""
    x: float
    y: float
    yaw: float  # heading in degrees
    timestamp: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DetectedObject:
    """Object detected by vision"""
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    camera_id: str
    timestamp: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LocalizedObject:
    """Object localized to 3D world coordinates"""
    label: str
    world_x: float
    world_y: float
    world_z: float
    confidence: float
    timestamp: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MotionState:
    """Robot motion tracking"""
    vx: float  # velocity X
    vy: float  # velocity Y
    omega: float  # angular velocity
    timestamp: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class StateManager:
    """
    Centralized state manager with thread-safe operations.
    All layers access and update state through this manager.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._status = SystemStatus.INITIALIZING
        
        # Core state
        self._robot_pose = RobotPose(x=0.0, y=0.0, yaw=0.0, timestamp=time.time())
        self._motion_state = MotionState(vx=0.0, vy=0.0, omega=0.0, timestamp=time.time())
        self._detected_objects: List[DetectedObject] = []
        self._localized_objects: List[LocalizedObject] = []
        
        # Observer pattern
        self._observers: Dict[str, List[Callable]] = {
            'robot_pose': [],
            'motion_state': [],
            'detected_objects': [],
            'localized_objects': [],
        }
        
        logger.info("StateManager initialized")
    
    # ========================================================================
    # ROBOT POSE
    # ========================================================================
    
    def update_robot_pose(self, x: float, y: float, yaw: float, source: str = "unknown"):
        """Update robot pose and notify observers"""
        with self._lock:
            self._robot_pose = RobotPose(x=x, y=y, yaw=yaw, timestamp=time.time())
            logger.info(f"Robot pose updated via {source}: ({x:.2f}, {y:.2f}, {yaw:.1f}°)")
            self._notify_observers('robot_pose', self._robot_pose)
    
    def get_robot_pose(self) -> RobotPose:
        """Get current robot pose (thread-safe copy)"""
        with self._lock:
            return copy.deepcopy(self._robot_pose)
    
    # ========================================================================
    # MOTION STATE
    # ========================================================================
    
    def update_motion_state(self, vx: float, vy: float, omega: float, source: str = "unknown"):
        """Update motion state"""
        with self._lock:
            self._motion_state = MotionState(vx=vx, vy=vy, omega=omega, timestamp=time.time())
            logger.info(f"Motion updated via {source}: vx={vx:.2f}, vy={vy:.2f}, omega={omega:.1f}")
            self._notify_observers('motion_state', self._motion_state)
    
    def get_motion_state(self) -> MotionState:
        """Get current motion state"""
        with self._lock:
            return copy.deepcopy(self._motion_state)
    
    # ========================================================================
    # DETECTED OBJECTS
    # ========================================================================
    
    def add_detected_object(self, obj: DetectedObject):
        """Add detected object"""
        with self._lock:
            self._detected_objects.append(obj)
            logger.info(f"Detected object: {obj.label} (confidence={obj.confidence:.2f})")
            self._notify_observers('detected_objects', self._detected_objects)
    
    def clear_detected_objects(self):
        """Clear all detected objects"""
        with self._lock:
            self._detected_objects.clear()
    
    def get_detected_objects(self) -> List[DetectedObject]:
        """Get all detected objects"""
        with self._lock:
            return copy.deepcopy(self._detected_objects)
    
    # ========================================================================
    # LOCALIZED OBJECTS
    # ========================================================================
    
    def add_localized_object(self, obj: LocalizedObject):
        """Add localized object"""
        with self._lock:
            self._localized_objects.append(obj)
            logger.info(f"Localized object: {obj.label} at ({obj.world_x:.2f}, {obj.world_y:.2f}, {obj.world_z:.2f})")
            self._notify_observers('localized_objects', self._localized_objects)
    
    def clear_localized_objects(self):
        """Clear all localized objects"""
        with self._lock:
            self._localized_objects.clear()
    
    def get_localized_objects(self) -> List[LocalizedObject]:
        """Get all localized objects"""
        with self._lock:
            return copy.deepcopy(self._localized_objects)
    
    # ========================================================================
    # OBSERVERS
    # ========================================================================
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to state change events"""
        with self._lock:
            if event_type in self._observers:
                self._observers[event_type].append(callback)
                logger.info(f"Observer subscribed to '{event_type}'")
    
    def _notify_observers(self, event_type: str, data: Any):
        """Notify all observers of a state change"""
        for callback in self._observers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Observer callback failed: {e}")
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def get_state_snapshot(self) -> Dict:
        """Get snapshot of entire state"""
        with self._lock:
            return {
                'robot_pose': self._robot_pose.to_dict(),
                'motion_state': self._motion_state.to_dict(),
                'detected_objects': [obj.to_dict() for obj in self._detected_objects],
                'localized_objects': [obj.to_dict() for obj in self._localized_objects],
            }
