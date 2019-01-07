import collections
import os
import pickle

from common.observation import *
from common.units import MILLISECOND, METER
from simulations.sim import Sim
from models.transmitControlSim import ModelTransmitControlData
from models.transmitDataSim import ModelTransmitData
import numpy as np


def get_max(model, headway):
    distances = model.leader.x - model.follower.x
    return max([abs(item - headway) for item in distances])

# Simulation with increasing clock_skew and delay.
# Only for Data and Future + Data
if __name__ == '__main__':
    save = True
    load = False
    iterations = 30000
    step_size = 1 * MILLISECOND
    headway = 30 * METER

    todo = np.full(iterations, -1, dtype=float)
    todo[4500] = 16.66
    todo[22000] = 0

    n = 11
    s = 0

    delay_step = 30
    noise_step = 30

    delays = [(s + delay_step * i) * MILLISECOND for i in range(n)]
    noises = [(s + noise_step * i) * MILLISECOND for i in range(n)]

    tmp_models = {}
    for delay in delays:
        tmp_models[delay] = {}
        for noise in noises:
            tmp_models[delay][noise] = [
                ModelTransmitData(iterations, headway, step_size, todo, noise, delay),
                ModelTransmitControlData(iterations, headway, step_size, todo, noise, delay),
            ]
    models = []

    for delay in delays:
        for noise in noises:
            models.extend(tmp_models[delay][noise])

    cache_path = f'../cache/{os.path.basename(__file__)}_{n}_{s}_{noise_step}_{delay_step}.pkl'

    if os.path.isfile(cache_path):
        with open(cache_path, 'rb') as file:
            tmp_models = pickle.load(file)
    else:
        s = Sim()
        s.run(models, iterations)
        with open(cache_path, 'wb') as output:
            pickle.dump(tmp_models, output, pickle.HIGHEST_PROTOCOL)

    com_delays = collections.OrderedDict()
    ctl_delays = collections.OrderedDict()

    errors = {}
    error_list = []
    delay_list = []
    noise_list = []
    errors_data = {}
    errors_com = {}
    errComb = [0, 0]
    minimal = 9999999
    together = 0
    n = 0
    for delay in tmp_models:
        errors[delay] = {}
        for noise in tmp_models[delay]:
            err = get_max(tmp_models[delay][noise][0], headway)
            errors[delay][noise] = err
            if err > errors[errComb[0]][errComb[1]]:
                errComb[0] = delay
                errComb[1] = noise
            if err < minimal:
                minimal = err
            together += err
            n += 1
    plot_surface(noises, delays, errors, "Delay (s)", "Clock skew (s)", "Error (m)", "", -120)
    print(type(tmp_models[delay][noise][0]).__name__)
    print(f"Max err: delay: {errComb[0]}, noise: {errComb[1]}, err: {errors[errComb[0]][errComb[1]]}")
    print(f"Min: {minimal}")
    print(f"Avg: {together/n}")

    errComb = [0, 0]
    minimal = 9999999
    n = 0
    minimal = 9999999
    together = 0
    n = 0
    for delay in tmp_models:
        errors[delay] = {}
        for noise in tmp_models[delay]:
            err = get_max(tmp_models[delay][noise][1], headway)
            errors[delay][noise] = err
            if err > errors[errComb[0]][errComb[1]]:
                errComb[0] = delay
                errComb[1] = noise
            if err < minimal:
                minimal = err
            together += err
            n += 1
    plot_surface(noises, delays, errors, "Delay (s)", "Clock skew (s)", "Error (m)", "", -120)
    print(type(tmp_models[delay][noise][1]).__name__)
    print(f"Model 1: Max err: delay: {errComb[0]}, noise: {errComb[1]}, err: {errors[errComb[0]][errComb[1]]}")
    print(f"Min: {minimal}")
    print(f"Avg: {together/n}")

    # how many in
    maximal = 0
    together = 0
    n = 0
    minimal = 9999999
    for delay in tmp_models:
        errors[delay] = {}
        for noise in tmp_models[delay]:
            errors[delay][noise] = how_many_not_in(tmp_models[delay][noise][0], headway)
            if errors[delay][noise] < minimal:
                minimal = errors[delay][noise]
            if errors[delay][noise] > maximal:
                maximal = errors[delay][noise]
            together += errors[delay][noise]
            n += 1
    plot_surface(noises, delays, errors, "Delay (s)", "Clock skew (s)", "Milliseconds not in charging area (ms)",
                 "", -120)
    print(f"Max err: {maximal}")
    print(f"Min: {minimal}")
    print(f"Avg: {together/n}")

    # how many in
    maximal = 0
    together = 0
    n = 0
    minimal = 9999999
    for delay in tmp_models:
        errors[delay] = {}
        for noise in tmp_models[delay]:
            errors[delay][noise] = how_many_not_in(tmp_models[delay][noise][1], headway)
            if errors[delay][noise] < minimal:
                minimal = errors[delay][noise]
            if errors[delay][noise] > maximal:
                maximal = errors[delay][noise]
            together += errors[delay][noise]
            n += 1
    plot_surface(noises, delays, errors, "Delay (s)", "Clock skew (s)", "Milliseconds not in charging area (ms)",
                 "", -120)
    print(f"Max err: {maximal}")
    print(f"Min: {minimal}")
    print(f"Avg: {together/n}")
