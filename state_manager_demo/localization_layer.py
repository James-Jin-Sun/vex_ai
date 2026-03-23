"""
Localization Layer
==================
Responsible for converting 2D detections to 3D world coordinates.
"""

import logging
from state_manager import StateManager, LocalizedObject, DetectedObject

logger = logging.getLogger(__name__)


class LocalalizationLayer:
    """Layer for localizing detected objects to 3D world space"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.state_manager.subscribe('detected_objects', self._on_detections)
        logger.info("LocalizationLayer initialized")
    
    def _on_detections(self, detections):
        """When new detections arrive, try to localize them"""
        logger.info(f"Localizing {len(detections)} detections")
        
        # Clear old localizations
        self.state_manager.clear_localized_objects()
        
        # For each detection, compute 3D world position (simplified)
        for detection in detections:
            # Placeholder: in reality would use stereo matching, calibration, etc.
            world_x = detection.bbox[0] * 0.5  # Simplified mapping
            world_y = detection.bbox[1] * 0.5
            world_z = 10.0  # Fixed height
            
            localized = LocalizedObject(
                label=detection.label,
                world_x=world_x,
                world_y=world_y,
                world_z=world_z,
                confidence=detection.confidence,
                timestamp=__import__('time').time()
            )
            self.state_manager.add_localized_object(localized)
