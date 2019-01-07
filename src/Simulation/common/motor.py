# Motor converts a unit less value between -1 and 1 to a value between min an max acceleration
class Motor:
    def __init__(self, max_acceleration, max_break):
        assert max_acceleration > 0 and max_break > 0, "max_acceleration and max_break must be positive"
        self.max_acceleration = max_acceleration
        self.max_break = max_break

    def get_acceleration(self, actual_velocity, percent):
        assert 1 >= percent >= -1, percent

        if actual_velocity > 0 and percent < 0:
            return self.max_break * percent

        else:
            return self.max_acceleration * percent
