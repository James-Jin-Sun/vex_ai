"""
Detection Layer
===============
Responsible for receiving raw vision data and updating detected objects.
"""

import logging
from state_manager import StateManager, DetectedObject

logger = logging.getLogger(__name__)


class DetectionLayer:
    """Layer for managing vision detections"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        # Subscribe to changes
        self.state_manager.subscribe('detected_objects', self._on_detection_change)
        logger.info("DetectionLayer initialized")
    
    def process_detection(self, label: str, confidence: float, bbox, camera_id: str):
        """Process and store detected object"""
        obj = DetectedObject(
            label=label,
            confidence=confidence,
            bbox=bbox,
            camera_id=camera_id,
            timestamp=__import__('time').time()
        )
        self.state_manager.add_detected_object(obj)
    
    def clear_detections(self):
        """Clear all detections for next frame"""
        self.state_manager.clear_detected_objects()
    
    def _on_detection_change(self, data):
        """Callback when detections change"""
        logger.debug(f"Detection change: {len(data)} objects")
