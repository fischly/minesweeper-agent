import argparse
import time
import random
import logging
import pickle
import codecs
import numpy as np

import sys
sys.path.insert(0, '.')

from minesweeper import Minesweeper

from solver_clingo import ClingoSolver
from solver_clingo_grouped import ClingoSolverGrouped
from solver_csp import CSPSolver
from solver_csp_grouped import CSPSolverGrouped


def get_seeded_instance(seed):
    np.random.seed(seed)
    m = Minesweeper(30, 16, 99)
    m.open(4,4)

    return m

def solve(solver):
    start_time = time.time()
    steps_done = 0

    while True:
        best_action = solver.solve_step()
        
        if solver.game.open(*best_action):
            break
        
        steps_done += 1

        solver.game.open_trivials()

        if solver.game.is_done():
            break

    time_diff = time.time() - start_time

    return solver.game.is_done(), time_diff, steps_done, solver.game.percentage_done()

def append_to_file(stats):
    with open('benchmark/bench.log', 'a') as myfile:
        pickled_b64 = codecs.encode(pickle.dumps(stats), 'base64').decode()
        myfile.write(pickled_b64 + '\n')

if __name__ == '__main__':
    solvers = [ClingoSolver, ClingoSolverGrouped, CSPSolver, CSPSolverGrouped]
    
    # clear previous benchmarks
    with open('benchmark/bench.log','w') as f:
        f.write('')    


    for i in range(1000):
        print(f'--- EPOCH {i + 1} --- ')
        seed = int(time.time() * 1000) % (2**32 - 1)
        
        for solver in solvers:
            # print(f'Starting solver "{solver.__name__} with seed {seed}..."')
            g = get_seeded_instance(seed)
            s = solver(g)

            try:
                result = (solver.__name__, seed, *solve(s))
                append_to_file(result)

                print(result)
            except:
                print('caugt exception')