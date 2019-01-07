import random

from common.communication import PacketAll
from common.units import MILLISECOND


# A sensor with delay and noise
class Sensor:
    def __init__(self, delay, noise):
        self.delay = delay
        self.delayTicks = int(self.delay / MILLISECOND)
        self.noise = noise
        self.last_packet = None

    def get_info(self, leader, frame):
        if frame - self.delayTicks > 0 and (self.delayTicks == 0 or frame % self.delayTicks == 0):
            if self.last_packet:
                dt = ((frame - self.delayTicks) - self.last_packet.timestamp) * MILLISECOND
                x = leader.x[frame - self.delayTicks] + random.normalvariate(0, self.noise)
                v = (x - self.last_packet.x) / dt
                a = (v - self.last_packet.v) / dt
                self.last_packet = PacketAll(a, v, x, frame - self.delayTicks)
            else:
                self.last_packet = PacketAll(leader.a[frame - self.delayTicks],
                                             leader.v[frame - self.delayTicks],
                                             leader.x[frame - self.delayTicks],
                                             frame - self.delayTicks)
        return self.last_packet
