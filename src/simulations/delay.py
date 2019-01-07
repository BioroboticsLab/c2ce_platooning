import os
import pickle
from common.observation import *
from common.units import MILLISECOND, METER, CENTIMETER
from models.sensorSim import ModelSensor
from models.transmitControlSensor import ModelTransmitControlSensor
from simulations.sim import Sim
from models.transmitControlSim import ModelTransmitControlData
from models.transmitDataSim import ModelTransmitData
import numpy as np

# Simulation without noises but with increasing delay
if __name__ == '__main__':
    iterations = 30000
    step_size = 1 * MILLISECOND
    headway = 30 * METER

    todo = np.full(iterations, -1, dtype=float)
    todo[4500] = 16.66
    todo[22000] = 0

    n = 11
    s = 0

    delay_step = 2

    delays = [(s + delay_step * (i + 0)) * MILLISECOND for i in range(n)]
    data_noise = 0 * MILLISECOND
    sens_noise = 0 * CENTIMETER

    sim_info = f"delay_step: {delay_step}ms, noise_sens{sens_noise}m, noise_data{data_noise}s"
    print(sim_info)

    # models = []
    tmp_models = {}
    for delay in delays:
        tmp_models[delay] = [
            ModelSensor(iterations, headway, step_size, todo, sens_noise, delay),
            ModelTransmitData(iterations, headway, step_size, todo, data_noise, delay),
            ModelTransmitControlSensor(iterations, headway, step_size, todo, sens_noise, data_noise, delay, delay),
            ModelTransmitControlData(iterations, headway, step_size, todo, data_noise, delay)
        ]
    models = []

    for delay in delays:
        models.extend(tmp_models[delay])

    cache_path = f'../cache/{os.path.basename(__file__)}_{n}_{s}_{delay_step}.pkl'

    if os.path.isfile(cache_path):
        with open(cache_path, 'rb') as file:
            tmp_models = pickle.load(file)
    else:
        s = Sim()
        s.run(models, iterations)
        with open(cache_path, 'wb') as output:
            pickle.dump(tmp_models, output, pickle.HIGHEST_PROTOCOL)

    # out = [[], []]
    # for delay in delays:
    #    out[0].append(get_max_err(tmp_models[delay][0], headway))
    #    out[1].append(get_max_err(tmp_models[delay][1], headway))

    # plot_err_mult(out, delays, ["Data", "Communication"])

    dif_models = len(tmp_models[delays[0]])
    # distances
    fig, plots = plt.subplots(dif_models, 1, sharex=True, sharey=True)

    for delay in delays:
        for i, model in enumerate(tmp_models[delay]):
            dists = model.leader.x - model.follower.x
            plots[i].plot([d - headway for d in dists])
            plots[i].set(xlabel='Time (s)', ylabel='Distance (m)')
            plots[i].label_outer()

    for i, model in enumerate(tmp_models[delays[0]]):
        plots[i].legend([model.follower.get_name()])
        plots[i].axhline(y=20 * CENTIMETER, linestyle="--", color="black", linewidth=1.0)
        plots[i].axhline(y=-20 * CENTIMETER, linestyle="--", color="black", linewidth=1.0)

    # plots[0].set_title("Distance / Time - " + sim_info)
    draw_or_save()

    # max error
    errs = np.zeros((dif_models, len(delays)))
    for d, delay in enumerate(delays):
        for i, model in enumerate(tmp_models[delay]):
            errs[i][d] = get_max_err(model, headway)

    legend = []
    for model in tmp_models[delays[0]]:
        legend.append(model.follower.get_name())

    fig, p = plt.subplots()

    for err in errs:
        p.plot(delays, err)
    p.legend(legend)
    p.set(xlabel='Delay (s)', ylabel='Error (m)')
    # p.set_title("Error / Delay - " + sim_info)
    draw_or_save()

    # jerk
    fig, plots = plt.subplots(dif_models, 1, sharex=True, sharey=True)

    for delay in delays:
        for i, model in enumerate(tmp_models[delay]):
            jerk = []
            for j in range(1, len(model.follower.a)):
                jerk.append(model.follower.a[j - 1] - model.follower.a[j])
            plots[i].plot(jerk)
            plots[i].set(xlabel='Time (s)', ylabel='Jerk (m/s^3)')
            plots[i].label_outer()

    for i, model in enumerate(tmp_models[delays[0]]):
        plots[i].legend([model.follower.get_name()])

    plots[0].set_title("Jerk / Time - " + sim_info)
    draw_or_save()

    # how many not in
    errs = np.zeros((dif_models, len(delays)))
    for d, delay in enumerate(delays):
        for i, model in enumerate(tmp_models[delay]):
            errs[i][d] = how_many_not_in(model, headway)

    legend = []
    for model in tmp_models[delays[0]]:
        legend.append(model.follower.get_name())

    fig, p = plt.subplots()

    for err in errs:
        p.plot(delays, err)
    p.legend(legend)
    p.set(xlabel='Delay (s)', ylabel='How many milliseconds not in charging area (ms)')
    draw_or_save()
