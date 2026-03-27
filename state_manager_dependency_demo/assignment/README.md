# Assignment: Expand Robot System with New Modules

This folder contains a working example using **RobotStateManager** with 9 modules total.

## Your Task

Study the existing modules and understand how they use **RobotStateManager** to coordinate without circular dependencies.

The 9 modules are organized in two groups:

### Core Vision & Motion (Already Implemented)
1. **vision_module.py** - Detects targets
2. **motion_module.py** - Controls robot movement
3. **intake_module.py** - Controls intake mechanism

### Scoring & Game Logic (Already Implemented)
4. **score_module.py** - Awards points when intake closes
5. **game_score_module.py** - Updates overall game score

### Communication & Coordination (Already Implemented)
6. **peer_to_peer_communication_module.py** - Communicates with allied robot
7. **teammate_state_module.py** - Coordinates teammate state
8. **opponent_position_module.py** - Detects opponent position

### Central State Management
9. **state_manager.py** - One source of truth for all robot state

## Key Learning Points

✓ **NO Circular Dependencies**: Each module only imports RobotStateManager (or other modules through it)
✓ **ONE Lock**: All thread-safety handled by RobotStateManager
✓ **Easy to Extend**: Adding new modules requires NO changes to existing code
✓ **Always Consistent**: All modules read from the same source of truth

## Module Dependencies

```
vision_module ──┐
                ├──→ RobotStateManager ←─── motion_module
intake_module ──┤
                ├──→ score_module ──→ game_score_module
                │
                ├──→ peer_to_peer_communication_module ──→ teammate_state_module
                │
                └──→ opponent_position_module
```

## Run the Complete System

```bash
python main.py
```

## Your Challenge

Once you understand this example:
1. Try removing RobotStateManager and see how hard it is to manage state
2. Add a 10th module for "strategy_module" that makes decisions based on all available state
3. See how easy it is to add without modifying existing code!

**Hint**: Strategy module should only need to query RobotStateManager, not import other modules.
