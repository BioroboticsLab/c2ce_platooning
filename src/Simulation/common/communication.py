import random
from typing import List

import numpy as np


class Packet:
    def __init__(self, timestamp: int):
        self.timestamp: int = timestamp


# All information
class PacketAll(Packet):
    def __init__(self, a: float, v: float, x: float, timestamp: int):
        self.a: float = a
        self.v: float = v
        self.x: float = x
        super().__init__(timestamp)


# The future behaviour of the leader
class PacketTodo(Packet):
    def __init__(self, v: float, timestamp: int):
        self.v: float = v
        super().__init__(timestamp)


# A car2car communication connection with latency and noise for the clock skew
class Connection:
    def __init__(self, latency: float, iterations: int, step_size: float, max_noise: float):
        self.latency: float = latency
        self.step_size = step_size
        self.latency_ticks: int = int(latency / step_size)
        self.dataStore = np.empty(iterations, dtype=Packet)
        self.outBuffer = []
        self.frame: int = 0
        self.max_noise = max_noise

    # write sends a new packet
    def write(self, packet: Packet):
        send_frame = self.frame + self.latency_ticks

        # clock skew
        packet.timestamp += -1 * abs(int(random.gauss(0.0, self.max_noise) / self.step_size))

        if send_frame == self.frame:
            self.outBuffer.append(packet)
        elif 0 <= send_frame < len(self.dataStore):
            if self.dataStore[send_frame] is None or \
                    not isinstance(self.dataStore[send_frame], PacketTodo):
                self.dataStore[send_frame] = packet

    def tick(self, frame):
        self.frame = frame
        if self.dataStore[self.frame] is not None:
            self.outBuffer.append(self.dataStore[self.frame])

    # read returns all available packets and flushes the buffer
    def read(self) -> List[Packet]:
        out = self.outBuffer.copy()
        self.outBuffer.clear()
        return out
