from common.sensor import Sensor
from common.communication import Connection, PacketTodo
from common.pid import PID, calc_ref_v
from common.units import *
from models.transmitControlSim import FollowerControlData, LeaderControlData


# A leader based on LeaderControlData that does not send the full state
class LeaderControlSensor(LeaderControlData):
    def tick(self, frame: int, time_passed: float):
        super().tick(frame, time_passed)
        if frame + self.horizonTicks < len(self.todo) and self.todo[frame + self.horizonTicks] != -1:
            self.connection.write(PacketTodo(self.todo[frame + self.horizonTicks], frame + self.horizonTicks))


# A follower that utilizes the sensor and the future.
class FollowerControlSensor(FollowerControlData):
    def __init__(self, iterations: int, connection: Connection, headway: float, leader, noise, sensor_delay):
        super().__init__(iterations, connection, headway)
        self.connection = connection

        self.sensor = Sensor(sensor_delay, noise)
        self.leader = leader

    def tick(self, frame: int, time_passed: float):
        packets = self.connection.read()
        for packet in packets:
            if isinstance(packet, PacketTodo):
                if packet.timestamp < frame:
                    self.pid.setpoint = packet.v
                else:
                    self.todo[packet.timestamp] = packet

        if self.todo[frame]:
            self.pid.setpoint = self.todo[frame].v
            self.last_todo = frame

        self.last_packet = self.sensor.get_info(self.leader, frame)

        if self.last_packet is not None:
            p = self.last_packet
            self.pid2.setpoint = calc_ref_v(self.headway, self.x[frame - 1], p.a, p.v, p.x,
                                            (frame - p.timestamp - 1) * MILLISECOND)

        super(FollowerControlData, self).tick(frame, time_passed)

    def drive(self, frame: int, time_passed: float):
        self.pid.compute(self.v[frame - 1])
        self.pid2.compute(self.v[frame - 1])

        sum = self.motor.get_acceleration(self.v[frame - 1], self.pid.output)
        sum += self.motor.get_acceleration(self.v[frame - 1], self.pid2.output)
        if sum > 4:
            sum = 4
        elif sum < -8:
            sum = -8
        self.a[frame] = sum

    def get_name(self):
        return "Future + Sensor"


class ModelTransmitControlSensor:
    def __init__(self, iterations: int, headway: float, step_size: float, todo, dist_noise, clock_noise, delay,
                 con_delay):
        self.iterations = iterations
        self.step_size = step_size
        self.noise = dist_noise
        self.delay = delay
        self.connection = Connection(con_delay, iterations, step_size, clock_noise)
        self.leader = LeaderControlSensor(iterations, self.connection, headway, todo)
        self.follower = FollowerControlSensor(iterations, self.connection, headway, self.leader, dist_noise, delay)

    def tick(self, frame):
        self.leader.tick(frame, self.step_size)
        self.follower.tick(frame, self.step_size)
        self.connection.tick(frame)
