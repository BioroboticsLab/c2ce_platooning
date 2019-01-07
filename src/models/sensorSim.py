from common.sensor import Sensor
from common.car import CarPID, Leader
from common.observation import *
from common.pid import calc_ref_v
from common.units import MILLISECOND


# A sensor based car. Get the information from the Sensor, calc the ref velocity and use it for the motor.
class FollowerSensor(CarPID):
    def __init__(self, iterations, leader: Car, headway: float, max_noise: float, delay: int):
        super().__init__(iterations, headway)

        self.pid.set_tuning(40.5, 0, 0.1, 1 * MILLISECOND)
        self.leader = leader
        self.sensor = Sensor(delay, max_noise)

    def tick(self, frame: int, time_passed: float):
        last_info = self.sensor.get_info(self.leader, frame)

        if last_info:
            self.pid.setpoint = calc_ref_v(self.headway, self.x[frame - 1],
                                           last_info.a,
                                           last_info.v,
                                           last_info.x,
                                           (frame - last_info.timestamp - 1) * MILLISECOND)

        super().tick(frame, time_passed)

    def get_name(self):
        return "Sensor"


class ModelSensor:
    def __init__(self, iterations: int, headway: float, step_size: float, todo, max_noise: float, delay: int):
        self.iterations = iterations
        self.step_size = step_size
        self.noise = max_noise
        self.delay = delay
        self.leader = Leader(iterations, headway, todo)
        self.follower = FollowerSensor(iterations, self.leader, headway, max_noise, delay)

    def tick(self, frame):
        self.leader.tick(frame, self.step_size)
        self.follower.tick(frame, self.step_size)
