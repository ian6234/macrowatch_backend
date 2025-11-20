import numpy as np


def fed_rate_odds(current_rate, forward_rate):

    possible_set = np.arange(-0.75, 0.75, 0.25)
    new_rates = possible_set + current_rate

    diff = new_rates - forward_rate

    diffs_sorted = np.sort(np.abs(diff))
    diffs_args = np.argsort(np.abs(diff))
    closest = diffs_sorted[0]
    closest_2 = diffs_sorted[1]

    odds_1 = 1 - closest/0.25
    odds_2 = 1 - closest_2/0.25

    odds = [[str(possible_set[diffs_args[0]]), float(odds_1.round(3))], [str(possible_set[diffs_args[1]]), float(odds_2.round(3))]]

    return odds


def macro_indexes(data):


    return data
