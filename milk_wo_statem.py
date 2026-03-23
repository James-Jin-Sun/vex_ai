import threading
import time
import copy
from dataclasses import dataclass

@dataclass
class FridgeState:
    """The 'Sticky Note' on the fridge."""
    milk_gallons: int = 0
    eggs_count: int = 0
    last_updated_by: str = "Initial"

class FridgeManager:
    def __init__(self):
        # 1. CENTRALIZED STATE
        self._state = FridgeState(milk_gallons=1, eggs_count=12)
        
        # 2. THE LOCK (The 'Magic Marker')
        # Only the person holding the marker can write on the fridge.
        self._lock = threading.Lock()

    def update_inventory(self, milk_diff, person_name):
        """Thread-safe update using a Lock."""
        print(f"🏠 {person_name} is checking the fridge...")
        
        with self._lock: 
            # 3. IMMUTABLE UPDATES (Work on a copy first)
            new_state = copy.deepcopy(self._state)
            
            # Simulate 'thinking' or 'shopping' time
            time.sleep(0.5) 
            
            new_state.milk_gallons += milk_diff
            new_state.last_updated_by = person_name
            
            # Save the new 'Sticky Note' over the old one
            self._state = new_state
            print(f"✅ {person_name} updated fridge: Milk is now {self._state.milk_gallons}")

    def check_fridge(self):
        """Thread-safe read."""
        with self._lock:
            return copy.deepcopy(self._state)

# --- SIMULATION ---

fridge = FridgeManager()

# Mom and Dad go shopping at the exact same time (Parallel Threads)
mom_thread = threading.Thread(target=fridge.update_inventory, args=(1, "Mom"))
dad_thread = threading.Thread(target=fridge.update_inventory, args=(1, "Dad"))

print("--- Start Shopping Day ---")
mom_thread.start()
dad_thread.start()

mom_thread.join()
dad_thread.join()

final_status = fridge.check_fridge()
print(f"--- End of Day ---")
print(f"Final Milk Count: {final_status.milk_gallons}")
print(f"Last person at the fridge: {final_status.last_updated_by}")