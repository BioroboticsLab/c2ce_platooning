import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from common.units import CENTIMETER
from .car import Car

_legend = []
_plots_drawn = 0

out = [0] * 10000

save = False


# helper methods for evaluation:

def get_max_err(model, headway):
    distances = model.leader.x - model.follower.x
    return max([abs(item - headway) for item in distances])


def get_mean(model, headway):
    distances = model.leader.x - model.follower.x
    distances = [abs(item - headway) for item in distances]
    return sum(distances) / len(distances)


def how_many_not_in(model, headway):
    distances = model.leader.x - model.follower.x
    many = 0
    for item in distances:
        d = abs(headway - item)
        if d > (20 * CENTIMETER):
            many += 1

    return many


# Generic plot methods:

def draw_or_save():
    global _plots_drawn
    if save:
        plt.savefig(f"../plots/plot_{_plots_drawn}.png")
    plt.show()
    _plots_drawn += 1


def draw_plot():
    plt.legend(_legend)
    draw_or_save()
    _legend.clear()


def draw_normal():
    plt.plot(out)
    draw_plot()


def plot_velocity(car1: Car, car2: Car):
    plt.title("Velocity")
    plt.ylabel("m/s")
    _legend.append(type(car1).__name__)
    _legend.append(type(car2).__name__)
    plt.plot(car1.v)
    plt.plot(car2.v)
    draw_plot()


def plot_acceleration(car1: Car, car2: Car):
    plt.title("Acceleration")
    plt.ylabel("m/s^2")
    _legend.append(type(car1).__name__)
    _legend.append(type(car2).__name__)
    plt.plot(car1.a)
    plt.plot(car2.a)
    draw_plot()


def plot_acceleration_one(car: Car):
    plt.title("Acceleration")
    plt.ylabel("m/s^2")
    _legend.append(type(car).__name__)
    plt.grid(True)
    plt.plot(car.a)
    draw_plot()


def plot_position(car1: Car, car2: Car):
    plt.title("Positions")
    plt.ylabel("m")
    _legend.append(type(car1).__name__)
    _legend.append(type(car2).__name__)
    plt.plot(car1.x)
    plt.plot(car2.x)
    draw_plot()


def plot_distance(car1: Car, car2: Car, headway: float):
    # plt.title("Distance")
    plt.ylabel("Distance (m)")
    plt.xlabel("ms")
    _legend.append(type(car1).__name__)
    _legend.append("Headway")

    plt.plot(car1.x - car2.x)

    ax = plt.axhline(headway)
    ax.set_color("black")
    ax.set_linestyle("--")
    draw_plot()


def plot_jerk(car: Car):
    plt.title("Jerk")
    plt.ylabel("m/s^3")
    _legend.append(type(car).__name__)

    car1j = []
    car2j = []
    for i in range(1, len(car.x)):
        car2j.append(car.a[i - 1] - car.a[i])

    plt.plot(car1j)
    plt.plot(car2j)
    draw_plot()


def print_result(car1: Car, car2: Car, headway: float):
    print(type(car1).__name__ + " | " + type(car2).__name__)
    distances = car1.x - car2.x
    print("Max distance", max(distances))
    print("Min distance", min(distances))
    print("Max error", max([abs(item - headway) for item in distances]))


def plot_distances(leader: Car, cars, headway: float):
    if not isinstance(cars, list):
        return plot_distance(leader, cars, headway)
    elif len(cars) <= 1:
        return plot_distance(leader, cars[0], headway)

    fig, plots = plt.subplots(len(cars), 1, sharex=True)
    plt.xlabel("ms")
    plt.ylabel("m")

    for i in range(len(cars)):
        plots[i].plot(leader.x - cars[i].x)
        plots[i].grid(True)
        plots[i].legend([type(cars[i]).__name__])

    draw_or_save()


def plot_accelerations(leader: Car, cars):
    if not isinstance(cars, list):
        return plot_acceleration(leader, cars)
    elif len(cars) <= 1:
        return plot_acceleration(leader, cars[0])

    fig, plots = plt.subplots(len(cars), 1, sharex=True)
    plt.xlabel("ms")
    plt.ylabel("m/s^2")

    for i in range(len(cars)):
        plots[i].plot(leader.a)
        plots[i].plot(cars[i].a)
        plots[i].grid(True)
        plots[i].legend([type(cars[i]).__name__])

    draw_or_save()


def plot_velocities(leader: Car, cars):
    if not isinstance(cars, list):
        return plot_velocity(leader, cars)
    elif len(cars) <= 1:
        return plot_velocity(leader, cars[0])

    fig, plots = plt.subplots(len(cars), 1, sharex=True)
    plt.xlabel("ms")
    plt.ylabel("m/s")

    for i in range(len(cars)):
        plots[i].plot(leader.v)
        plots[i].plot(cars[i].v)
        plots[i].grid(True)
        plots[i].legend([type(cars[i]).__name__])

    draw_or_save()


def plot_positions(leaders, cars):
    if len(cars) <= 1:
        return plot_position(leaders[0], cars[0])
    fig, plots = plt.subplots(len(cars), 1, sharex=True)
    plt.xlabel("ms")
    plt.ylabel("m")

    for i in range(len(cars)):
        plots[i].plot(leaders[i].x)
        plots[i].plot(cars[i].x)
        plots[i].grid(True)
        plots[i].legend([type(cars[i]).__name__, "Headway"])

    draw_or_save()


def plot_jerks(cars):
    if len(cars) <= 1:
        return plot_position(cars[0])
    fig, plots = plt.subplots(len(cars), 1, sharex=True)
    plt.xlabel("ms")
    plt.ylabel("m/s^3")
    plt.title("Jerk")
    plt.axhline(y=2, color='r')
    plt.axhline(y=-2, color='r')

    for i in range(len(cars)):
        car = cars[i]
        jerk = np.zeros(len(car.a), float)
        for ai in range(len(car.a) - 1):
            jerk[ai] = car.a[ai] - car.a[ai + 1]

        plots[i].plot(jerk)
        plots[i].grid(True)
        plots[i].legend(["headway 2", "headway -2", type(cars[i]).__name__, "Headway"])

    draw_or_save()


def plot_noise(noises, counts, verticalName, titel):
    plt.xlabel("max error")
    plt.ylabel(verticalName)
    plt.title(titel + ": Error - " + verticalName)
    plt.yticks([i for i in range(len(noises))], noises)
    # plt.plot(noise)

    plt.barh([i for i in range(len(noises))], counts, align='center', edgecolor="black")
    draw_or_save()


# format: model, noise level, max dist, how much error?


def plot_color_graph(inputs, input_names=[], input_noises=[], ylabel="noise"):
    height = min([len(x) for x in inputs])
    data = np.zeros((height, len(inputs)))

    for i in range(height):
        for j in range(len(inputs)):
            data[i][j] = inputs[j][i]

    print(data)
    c = plt.pcolor(data, cmap='RdBu', )

    plt.xticks([i + 0.5 for i in range(len(input_names))], input_names)
    plt.yticks([i + 0.5 for i in range(len(input_noises))], input_noises)

    plt.ylabel(ylabel)
    plt.xlabel("Model")

    plt.tight_layout()
    plt.colorbar(c)
    plt.show()


def plot_diff(inputs):
    x = list(inputs.keys())
    y = list(inputs.values())
    plt.plot(x, y)
    plt.title("max(data.err) - max(communication.error)")
    draw_or_save()


def plot_err_mult(errors, delays, names):
    i = 0
    for err in errors:
        plt.plot(delays, err)
        _legend.append(names[i])
        i += 1

    plt.title("Error / Delay")
    draw_plot()


def plot_surface(noises, delays, inputs, xlabel, ylabel, zlabel, titel="", rotation=20):
    x, y = np.meshgrid(noises, delays)
    z = np.zeros((len(delays), len(noises)), dtype=float)

    delay_i = 0
    noise_i = 0
    for delay in delays:
        for noise in noises:
            z[delay_i][noise_i] = inputs[delay][noise]
            noise_i += 1
        delay_i += 1
        noise_i = 0

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    ax.set_title(titel)

    surf = ax.plot_surface(y, x, z, shade=True, cmap='RdBu')
    fig.colorbar(surf)

    ax.view_init(30, rotation)
    draw_or_save()


def plot_trisurface(noises, delays, errors):
    print(noises)
    print(delays)

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('Delays')
    ax.set_ylabel('Noises')
    ax.set_zlabel('max(error(data)) - max(error(communication))')

    print(noises, delays, errors)
    surf = ax.plot_trisurf(delays, noises, errors, shade=True, cmap='RdBu')
    fig.colorbar(surf)

    ax.view_init(30, 20)
    draw_or_save()
