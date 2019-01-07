import numpy as np

from common.car import Leader, CarPID
from common.communication import Connection, PacketTodo, PacketAll, Packet
from common.pid import PID, calc_ref_v
from common.units import *


# A leader that sends the future and the full state to the follower
class LeaderControlData(Leader):
    def __init__(self, iterations: int, connection: Connection, headway: float, todo):
        super().__init__(iterations, headway, todo)
        self.horizon = 15 * MILLISECOND
        self.connection = connection
        self.horizonTicks = int(self.horizon / MILLISECOND)

    def tick(self, frame: int, time_passed: float):
        super().tick(frame, time_passed)
        self.connection.write(PacketAll(self.a[frame], self.v[frame], self.x[frame], frame))
        if frame + self.horizonTicks < len(self.todo) and self.todo[frame + self.horizonTicks] != -1:
            self.connection.write(PacketTodo(self.todo[frame + self.horizonTicks], frame + self.horizonTicks))


# Follower utilizing the future and the full state.
class FollowerControlData(CarPID):
    def __init__(self, iterations: int, connection: Connection, headway: float):
        super().__init__(iterations, headway)
        self.connection = connection

        self.todo = np.full(iterations, None, dtype=PacketTodo)
        self.last_packet: PacketTodo = None
        self.pid.set_tuning(0.25, 0.0, 0.0, 1 * MILLISECOND)
        self.pid.out_max = 0.75  # like leader
        self.motor.max_acceleration = 4
        self.motor.max_break = 8
        self.last_todo = 0

        # Second PID for the data transmission
        self.pid2 = PID()
        self.pid2.set_tuning(1.0, 0.0, 0.0, 1 * MILLISECOND)
        self.pid2.out_min = -1
        self.pid2.out_max = 1

    def receive(self, packets):
        found: Packet = self.last_packet
        for packet in packets:
            if isinstance(packet, PacketAll):
                if found is None or found.timestamp < packet.timestamp:
                    found = packet
        self.last_packet = found

    def tick(self, frame: int, time_passed: float):
        packets = self.connection.read()
        for packet in packets:
            if isinstance(packet, PacketTodo):
                if packet.timestamp < frame:
                    self.pid.setpoint = packet.v
                else:
                    self.todo[packet.timestamp] = packet
        self.receive(packets)

        if self.todo[frame]:
            self.pid.setpoint = self.todo[frame].v
            self.last_todo = frame

        if self.last_packet is not None:
            p = self.last_packet
            self.pid2.setpoint = calc_ref_v(self.headway, self.x[frame - 1], p.a, p.v, p.x,
                                            (frame - p.timestamp - 1) * MILLISECOND)

        super().tick(frame, time_passed)

    def drive(self, frame: int, time_passed: float):
        # mix both PIDs
        self.pid.compute(self.v[frame - 1])
        self.pid2.compute(self.v[frame - 1])
        sum = 0
        sum += self.motor.get_acceleration(self.v[frame - 1], self.pid.output)
        sum += self.motor.get_acceleration(self.v[frame - 1], self.pid2.output)
        if sum > 4:
            sum = 4
        elif sum < -8:
            sum = -8
        self.a[frame] = sum

    def get_name(self):
        return "Future + Data"


class ModelTransmitControlData:
    def __init__(self, iterations: int, headway: float, step_size: float, todo, com_noise, delay):
        self.iterations = iterations
        self.step_size = step_size
        self.noise = com_noise
        self.delay = delay
        self.connection = Connection(delay, iterations, step_size, com_noise)
        self.leader = LeaderControlData(iterations, self.connection, headway, todo)
        self.follower = FollowerControlData(iterations, self.connection, headway)

    def tick(self, frame):
        self.leader.tick(frame, self.step_size)
        self.follower.tick(frame, self.step_size)
        self.connection.tick(frame)
