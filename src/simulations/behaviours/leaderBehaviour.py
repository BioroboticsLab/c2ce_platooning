from common.observation import *
from common.units import MILLISECOND, METER, CENTIMETER
from models.sensorSim import ModelSensor
from simulations.sim import Sim


def get_max(model, headway):
    distances = model.leader.x - model.follower.x
    return max([abs(item - headway) for item in distances])


if __name__ == '__main__':
    iterations = 30000
    step_size = 1 * MILLISECOND
    headway = 30 * METER

    todo = np.full(iterations, -1, dtype=float)
    todo[4500] = 16.66
    todo[22000] = 0

    delay = 50
    models = [ModelSensor(iterations, headway, step_size, todo, 0 * CENTIMETER, 0 * MILLISECOND)]

    print("Setting up threads")
    s = Sim()
    s.run(models, iterations)

    for model in models:
        print_result(model.leader, model.follower, headway)

    plt.title("Velocity")
    plt.ylabel("Velocity (m/s)")
    plt.plot(models[0].leader.v)
    plt.xlabel("Time (ms)")
    draw_plot()

    plt.title("Acceleration")
    plt.ylabel("Acceleration (m/s^2)")
    plt.xlabel("Time (ms)")
    plt.plot(models[0].leader.a)
    draw_plot()

    plot_distance(models[0].leader, models[0].follower, headway)
