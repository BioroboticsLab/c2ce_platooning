import numpy as np

from common.motor import Motor
from common.pid import PID
from common.units import MILLISECOND


# Car defines the base class for all cars
class Car:
    def __init__(self, iterations: int, headway: float):
        self.x = np.zeros(iterations, dtype=float)
        self.v = np.zeros(iterations, dtype=float)
        self.a = np.zeros(iterations, dtype=float)
        self.headway = headway

    def tick(self, frame: int, time_passed: float):
        self.v[frame] = self.v[frame - 1] + self.a[frame] * time_passed
        self.x[frame] = self.x[frame - 1] + self.v[frame] * time_passed


# A Car that is controlled by a PID
class CarPID(Car):
    def __init__(self, iterations: int, headway: float):
        super().__init__(iterations, headway)
        self.pid = PID()
        self.pid.out_min = -1
        self.pid.out_max = 1
        self.motor = Motor(4, 8)

    def tick(self, frame: int, time_passed: float):
        self.drive(frame, time_passed)
        super().tick(frame, time_passed)

    # For override reasons an extra method
    def drive(self, frame: int, time_passed: float):
        self.pid.compute(self.v[frame - 1])
        self.a[frame] = self.motor.get_acceleration(self.v[frame - 1], self.pid.output)


# Leader has a todolist of pid setpoints with reference velocities
class Leader(CarPID):
    def __init__(self, iterations: int, headway: float, todo):
        super().__init__(iterations, headway)
        self.todo = todo
        self.x[0] = self.headway  # start with the correct offset

        self.pid.set_tuning(0.25, 0.0, 0.0, 1 * MILLISECOND)
        self.pid.out_max = 0.75  # max acceleration is then scaled to 3
        self.motor.max_acceleration = 4

    def tick(self, frame: int, time_passed: float):
        if self.todo[frame] != -1:
            self.pid.setpoint = self.todo[frame]

        super().tick(frame, time_passed)
