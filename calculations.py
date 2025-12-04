import numpy as np


# calculates forward rate between two bonds e.g. (1mo vs 3mo uk gilt)
def calc_forward_rate(rate_1, rate_2, time_1, time_2):
    del_time = time_2 - time_1
    # (1+rate_1)^time_1 * (1+fwd_rate)^del_time = (1+rate_2)^time_2
    fwd_rate = ((1+rate_2)**time_2 / (1+rate_1)**time_1)**(1/del_time)
    return fwd_rate-1


# linear interpolation of rate decision based on current and forward interest rate
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
