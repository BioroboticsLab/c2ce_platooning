# http://brettbeauregard.com/blog/2011/04/improving-the-beginner’s-pid-reset-windup/


class PID:
    def __init__(self):
        self.setpoint: float = 0
        self._last_input: float = 0
        self.output: float = 0
        self._i_term: float = 0
        self._kp: float = 0
        self._kd: float = 0
        self._ki: float = 0

        self.out_min: float = 0
        self.out_max: float = 0

    def compute(self, input: float):
        error = self.setpoint - input
        self._i_term += self._ki * error
        if self._i_term > self.out_max:
            self._i_term = self.out_max
        elif self._i_term < self.out_min:
            self._i_term = self.out_min

        d_input = input - self._last_input

        self.output = self._kp * error + self._i_term - self._kd * d_input
        if self.output > self.out_max:
            self.output = self.out_max
        elif self.output < self.out_min:
            self.output = self.out_min

        self._last_input = input

    def set_tuning(self, kp: float = None, ki: float = None, kd: float = None, sample_time: float = None):
        self._kp = kp
        if ki is not None and sample_time:
            self._ki = ki * sample_time
        if kd is not None and sample_time:
            self._kd = kd / sample_time


# Reference velocity calculation
def calc_ref_v(headway: float, self_x: float, leader_a: float, leader_v: float, leader_x: float, age: float) -> float:
    # extrapolate the old information
    leader_x += leader_a / 2 * age ** 2 + leader_v * age
    leader_v += leader_a * age

    dist = leader_x - self_x
    return leader_v + dist - headway
