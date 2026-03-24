# Owns target_found state, but other modules import this directly.

target_found = False

def detect_target(is_visible):
    global target_found
    target_found = is_visible

