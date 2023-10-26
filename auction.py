import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def add_item(type):
    buildings[type] = buildings[type] + 1
    new_data[type] = data[type] * buildings[type]


def get_energy_losses():
    return new_data["Больницы"] + new_data["Заводы"] + new_data["Дома"]


def get_energy_income():
    return new_data["Солнце"] + new_data["Ветер"]


def plot_energy_income():
    plt.subplot(1, 2, 1)
    plt.plot(get_energy_income())
    plt.plot(get_energy_losses())
    plt.legend(["Генераторы", "Потребители"])
    plt.draw()


def plot_energy():
    # fig, axes = plt.subplots(1, 2)
    # axes[1].cla()
    plt.clf()
    plt.subplot(1, 2, 2)
    plt.plot(new_data)
    plt.legend(new_data.columns)
    plt.draw()

# TODO: учет размера накопителя и сколько он может отдавать за такт


def count_energy_losses():
    return np.sum(get_energy_income() - get_energy_losses())


data = pd.read_csv("forecast.csv", sep="\t")
data = data.drop(data.columns[[0]], axis=1)

new_data = data.copy()
new_data = new_data * 0
buildings = {"Солнце": 0, "Ветер": 0, "Больницы": 0, "Заводы": 0, "Дома": 0}
plt.ion()
while True:

    item = input("Input object name: ")
    add_item(item)
    print("Energy losses: " + str(count_energy_losses()))

    plot_energy()
    plot_energy_income()
