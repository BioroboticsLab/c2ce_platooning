from common.observation import *
from common.units import MILLISECOND, METER
from models.transmitControlSim import ModelTransmitControlData
from simulations.sim import Sim

if __name__ == '__main__':
    iterations = 30000
    step_size = 1 * MILLISECOND
    headway = 30 * METER

    todo = np.full(iterations, -1, dtype=float)
    todo[4500] = 16.66
    todo[22000] = 0

    models = [ModelTransmitControlData(iterations, headway, step_size, todo, 15 * MILLISECOND, 30 * MILLISECOND, )]

    print("Setting up threads")
    s = Sim()
    s.run(models, iterations)

    for model in models:
        print_result(model.leader, model.follower, headway)
        many = how_many_not_in(model, headway)

        # plot_jerks([models[0].leader] + [model.follower for model in models])
        # plot_accelerations(models[0].leader, [model.follower for model in models])
        # plot_velocities(models[0].leader, [model.follower for model in models])
        # plot_positions([model.leader for model in models], [model.follower for model in models])
        # plot_distances(model.leader, [model.follower for model in models], headway)

        dists = model.leader.x - model.follower.x
        plt.plot([d - headway for d in dists])
        plt.xlabel("Time (ms)")
        plt.ylabel('Distance (m)')

        plt.legend([model.follower.get_name()])
        plt.axhline(y=20 * CENTIMETER, linestyle="--", color="black", linewidth=1.0)
        plt.axhline(y=-20 * CENTIMETER, linestyle="--", color="black", linewidth=1.0)

        # plots[0].set_title("Distance / Time - " + sim_info)
        draw_or_save()
