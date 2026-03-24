# Needs target_found from vision_module and motion_state from motion_module.
# Also manages intake_state.
# This creates a circular dependency because motion_module imports intake_module too.

import vision_module
import motion_module

intake_state = "open"

def update_intake_state():
    global intake_state
    if vision_module.target_found and motion_module.motion_state == "chasing":
        intake_state = "closing"
    else:
        intake_state = "open"

