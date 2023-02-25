import time
import random
import logging
import pickle
import codecs
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

from solver_clingo import ClingoSolver
from solver_clingo_grouped import ClingoSolverGrouped
from solver_csp import CSPSolver
from solver_csp_grouped import CSPSolverGrouped


def load_runs(file):
    with open(file, 'r') as myfile:
        content = myfile.read()
        runs = content.split('\n\n')
        runs = list(filter(lambda r: r != '', runs))

        runs = list(map(
            lambda run: pickle.loads(codecs.decode(bytes(run, 'utf-8'), 'base64')),
            runs
        ))

        grouped_by_seed = defaultdict(list)
        for i, (solver, seed, success, duration, steps, percentage) in enumerate(runs):
            grouped_by_seed[seed].append((solver, success, duration, steps, percentage))

        grouped_by_solver = defaultdict(list)
        for i, (solver, seed, success, duration, steps, percentage) in enumerate(runs):
            grouped_by_solver[solver].append((seed, success, duration, steps, percentage))

        return runs, grouped_by_seed, grouped_by_solver

def get_bins(runs):
    bin_values = [5**x for x in range(-2, 6)] #[10**x for x in range(-1, 5)]

    bins = defaultdict(int)
    for value in bin_values:
        bins[value] = 0

    for seed, success, duration, steps, percentage in runs:
        for value in bin_values:
            if duration < value:
                # bins[value].append(run)
                bins[value] += 1
                break

    return bin_values, bins

def get_statistics(runs):
    durs = [duration for seed, success, duration, steps, percentage in runs]

    min_val = min(durs)
    max_val = min(durs)

    average = np.mean(durs)
    median = np.median(durs)
    std = np.std(durs)

    return min_val, max_val, average, median, std



if __name__ == '__main__':
    runs, grouped_by_seed, grouped_by_solver = load_runs('bench.log')

    fig, axs = plt.subplots(2, 2)
    
    for i, solver in enumerate(['ClingoSolver', 'ClingoSolverGrouped', 'CSPSolver', 'CSPSolverGrouped']):
        bin_values, bins = get_bins(grouped_by_solver[solver])
        min_val, max_val, average, median, std = get_statistics(grouped_by_solver[solver])

        ax = axs[i % 2, i // 2]

        ax.bar([f'< {str(value)}s' for value in bin_values], list(bins.values()))
        ax.axis(ymax=350)
        ax.set_title(solver)
        ax.set(ylabel='instances')
        ax.bar_label(ax.containers[0])

        ax.text(5, 300, 'Mean: {:0.2f}s'.format(average), fontsize=12)
        ax.text(5, 270, 'Median: {:.2f}s'.format(median), fontsize=12)
        ax.text(5, 240, 'Std.Dev.: {:.2f}s'.format(std), fontsize=12)

    plt.margins(x=0)
    plt.show() 