import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from collections import defaultdict

types = {'s': 'sun',
         'w': 'wind',
         'l': 'living',
         'f': 'factory',
         'h': 'hospital'}

ACCUMULATOR_C = 150
ACCUMULATOR_S = 10


def add_item(type, cost):

    if type not in types.keys():
        return False
    type = types[type]
    buildings[type].append(int(cost))
    new_data[type] = data[type] * len(buildings[type])
    return True


def remove_item(type, cost=-1):
    type = types[type]
    if cost > -1:
        buildings[type].remove(cost)
    else:
        buildings[type].pop()
    new_data[type] = data[type] * len(buildings[type])


def get_energy_wasters():
    return new_data["hospital"] + new_data["factory"] + new_data["living"]


def get_energy_generators():
    return new_data["sun"] + new_data["wind"]


def count_energy_losses():
    losses = np.sum(get_energy_generators() - get_energy_wasters())
    return losses


def count_stonks(energy_sold, last_acc):
    def count_income(type): return np.sum(buildings[type]) * new_data[type]
    def count_losses(type): return np.sum(buildings[type]) * new_data.shape[0]
    everything = []
    for type in buildings.keys():
        if type == 'wind' or type == 'sun':
            everything.append(count_losses(type))
        else:
            everything.append(count_income(type))
    losses = np.sum(everything[:2])
    # print(energy_sold)
    income = np.sum(everything[2:]) + 2 * (np.sum(energy_sold) + last_acc)
    return income - losses


def plot_energy_income():
    plt.subplot(1, 2, 1)
    plt.plot(get_energy_generators())
    plt.plot(get_energy_wasters())
    plt.legend(["Генераторы", "Потребители"])
    plt.draw()


def plot_energy():
    # fig, axes = plt.subplots(1, 2)
    # axes[1].cla()
    plt.clf()
    plt.subplot(1, 2, 2)
    plt.plot(new_data)
    c_names = []
    plt.legend(new_data.columns)
    plt.draw()


def get_accumulated_energy():
    wasters = get_energy_wasters() * 1.25
    gens = get_energy_generators() * 0.83
    diff = pd.Series.to_numpy(gens - wasters)
    cumsum = np.cumsum(diff)
    diffs = cumsum - np.insert(cumsum, 0, 0)[:-1]
    while np.max(diffs) > ACCUMULATOR_S:
        first_big_diff = np.where(diffs > ACCUMULATOR_S)[0][0]
        cumsum[first_big_diff:] = cumsum[first_big_diff:] - \
            (diff[first_big_diff] - ACCUMULATOR_S)
        diffs = cumsum - np.insert(cumsum, 0, 0)[:-1]

    discarded_turn = []
    discarded = []
    while np.max(cumsum) > ACCUMULATOR_C:
        first_max_idx = np.where(cumsum > ACCUMULATOR_C)[0][0]
        discarded_turn.append(first_max_idx)
        discarded.append(cumsum[first_max_idx] - ACCUMULATOR_C)
        cumsum[first_max_idx:] = cumsum[first_max_idx:] - \
            (cumsum[first_max_idx] - ACCUMULATOR_C)
    discarded = np.array(discarded)
    return cumsum, discarded, discarded_turn


def get_turns(discarded_turn, acc_last):
    result = {}
    for idx, i in enumerate(discarded_turn):
        result[i] = discarded[idx]
    if acc_last > 0:
        result[169] = acc_last

    return result


data = pd.read_csv("forecast.csv", sep="\t")
data = data.drop(data.columns[[0]], axis=1)
data = data.rename(columns={'Солнце': 'sun', 'Ветер': 'wind', 'Больницы': 'hospital',
                            'Заводы': 'factory', 'Дома': 'living'})
data['sun'] = data['sun'] * 2
data['wind'] = data['wind'] * 1.5

new_data = data.copy()
new_data = new_data * 0
buildings = {"sun": [], "wind": [],
             "hospital": [], "factory": [], "living": []}

plt.ion()

prev_item = ''
accumulated, discarded, discarded_turn = [], [], []
while True:
    item = ''
    cost = 0
    while not add_item(item, cost):
        inp = input("Input object name: ")
        args = inp.split(' ')
        if args[0] == 'rm':
            if len(args) == 1:
                remove_item(prev_item)
            else:
                remove_item(args[1], int(args[2]))
            break
        elif args[0] == 'sell':
            for idx, i in enumerate(discarded_turn):
                print('Turn: ', i, ', value:',
                      discarded[idx])
            if accumulated[-1] > 0:
                print('Turn: last', ', value:', accumulated[-1])
        else:
            item, cost = args[0], args[1]
            prev_item = item
    accumulated, discarded, discarded_turn = get_accumulated_energy()

    print('===========================================')
    print('ENERGY LOSSES: ' + "%.0f" % -count_energy_losses() + ' -----> ' +
          ('OK' if count_energy_losses() > 0 else 'Маловато будет'))
    print('+++++++++++++++++++++++++++++++++++++++++++')
    print('STONKS: ' + "%.0f" % count_stonks(discarded, accumulated[-1]))
    print('===========================================\n')

    plot_energy()
    plot_energy_income()
