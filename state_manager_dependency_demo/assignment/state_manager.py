# robot_state_manager.py
# One place for all VEX AI robot shared state.

class RobotStateManager:
    def __init__(self):
        self.target_found = False
        self.motion_state = "idle"
        self.intake_state = "open"
        self.score = 0
        self.ally_robot_position = None
        self.opponent_position = None
        self.game_score = 0

    def detect_target(self, is_visible):
        self.target_found = is_visible

    def update_motion_state(self):
        if self.target_found:
            self.motion_state = "chasing"
        else:
            self.motion_state = "searching"

    def update_intake_state(self):
        if self.target_found and self.motion_state == "chasing":
            self.intake_state = "closing"
        else:
            self.intake_state = "open"

    def score_points(self, points):
        self.score += points

    def set_ally_position(self, position):
        self.ally_robot_position = position

    def get_ally_position(self):
        return self.ally_robot_position

    def set_opponent_position(self, position):
        self.opponent_position = position

    def update_game_score(self, score):
        self.game_score = score

