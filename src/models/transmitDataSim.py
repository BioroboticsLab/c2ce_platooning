from common.car import CarPID, Leader
from common.communication import Connection, PacketAll, Packet
from common.pid import calc_ref_v
from common.units import *


# Leader that sends data to the follower
class LeaderData(Leader):
    def __init__(self, iterations: int, connection: Connection, headway: float, todo):
        super().__init__(iterations, headway, todo)
        self.connection = connection

    def tick(self, frame: int, time_passed: float):
        super().tick(frame, time_passed)
        self.connection.write(PacketAll(self.a[frame], self.v[frame], self.x[frame], frame))


# Follower using the data from the leader
class FollowerData(CarPID):
    def __init__(self, iterations: int, connection: Connection, headway: float):
        super().__init__(iterations, headway)
        self.connection = connection
        self.pid.set_tuning(40.5, 0, 0.1, 1 * MILLISECOND)
        self.last_packet = None

    def tick(self, frame: int, time_passed: float):
        self.receive(self.connection.read())
        self.update_pid(frame, self.pid)
        super().tick(frame, time_passed)

    def receive(self, packets):
        found: Packet = self.last_packet
        for packet in packets:
            if isinstance(packet, PacketAll):
                if found is None or found.timestamp < packet.timestamp:
                    found = packet
        self.last_packet = found

    def update_pid(self, frame, pid):
        if self.last_packet is not None:
            p = self.last_packet
            pid.setpoint = calc_ref_v(self.headway, self.x[frame - 1], p.a, p.v, p.x,
                                      (frame - p.timestamp - 1) * MILLISECOND)

    def get_name(self):
        return "Data"


class ModelTransmitData:
    def __init__(self, iterations: int, headway: float, step_size: float, todo, com_noise, com_delay):
        self.iterations = iterations
        self.noise = com_noise
        self.step_size = step_size
        self.delay = com_delay
        self.connection = Connection(com_delay, iterations, step_size, com_noise)
        self.leader = LeaderData(iterations, self.connection, headway, todo)
        self.follower = FollowerData(iterations, self.connection, headway)

    def tick(self, frame):
        self.leader.tick(frame, self.step_size)
        self.follower.tick(frame, self.step_size)
        self.connection.tick(frame)
