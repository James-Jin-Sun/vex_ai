# Bad Example

This version shows the dependency mess in a VEX AI robot:

- `vision_module` owns `target_found`
- `motion_module` needs `vision_module.target_found` and controls `motion_state`
- `gripper_module` needs both `vision_module.target_found` and `motion_module.motion_state`, then controls `gripper_state`
- `subsystem_monitor` needs all three states from three different modules
- `motion_module` also imports `gripper_module`, creating a circular dependency

So even with very small code, the robot component references become hard to manage.
