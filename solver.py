import argparse
import time
import random
import logging
import numpy as np

from minesweeper import Minesweeper
from solver_clingo import ClingoSolver
from solver_clingo_grouped import ClingoSolverGrouped
from solver_csp import CSPSolver
from solver_csp_grouped import CSPSolverGrouped


if __name__ == '__main__':
    # logging stuff
    logging.basicConfig()
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(fmt=' %(name)s :: %(levelname)-8s :: %(message)s'))
    logging.getLogger().addHandler(ch)

    # parsing arguments
    parser = argparse.ArgumentParser(prog='python3 solver.py', description='Solves a randomly generated minesweeper instance')
    parser.add_argument('-w', '--width', help='The width of the minesweeper instance', type=int, default=30) 
    parser.add_argument('-he', '--height', help='The height of the minesweeper instance', type=int, default=16) 
    parser.add_argument('-b', '--bombs', help='The number of bombs of the minesweeper instance', type=int, default=99) 
    parser.add_argument('-s', '--seed', help='Fixes the seed to generate the random minesweeper instance', type=int) 
    parser.add_argument('--solver', choices=['clingo', 'clingo-grouped', 'csp', 'csp-grouped'], const='clingo-grouped', default='clingo-grouped', nargs='?', help='The solving approach to use')
    parser.add_argument('--no-trivial', help='If set, do not perform trivial cell opening/marking', action='store_true')
    parser.add_argument('-d', '--delay', help='Delay in milliseconds between performing actions', type=int) 
    parser.add_argument('-i', '--interactive', help='If set, waits for user input between each action', action='store_true')

    args = parser.parse_args()
    print(args)

    # fix random seed
    seed = int(time.time() * 1000) % (2**32 - 1) if args.seed is None else args.seed
    print('Seed: ', seed)
    np.random.seed(seed)

    # initialize the minesweeper instance
    g = Minesweeper(args.width, args.height, args.bombs)

    # open the first field (so the solver has something to go on)
    if g.open(*(2, 2) if args.width >= 3 and args.height >= 3 else (0, 0)):
        print('Game lost on first cell opened :(')
        exit()

    # instantiate the solver given as argument
    solver_tuples = [('clingo', ClingoSolver), ('clingo-grouped', ClingoSolverGrouped), ('csp', CSPSolver), ('csp-grouped', CSPSolverGrouped)]

    for solver_name, solver_class in solver_tuples:
        if args.solver == solver_name:
            s = solver_class(g)

    if not s:
        assert False, f'solver "{args.solver}" not implemented'
        

    start_time = time.time()
    steps_done = 1

    while True:
        best_action = s.solve_step()
        print(f'--- OPENING {best_action} ---')

        if g.open(*best_action):
            print('\n===== GAME OVER =====')
            break
        
        steps_done += 1

        if not args.no_trivial:
            g.open_trivials()

        if g.is_done():
            print('\n===== WON =====')
            print(g)
            break

        print(g)

        if args.interactive:
            input('Press a key to perform next action...')
        elif args.delay is not None:
            time.sleep(args.delay / 1000)

    if not args.interactive:
        print('--- {0:.2f} seconds ---'.format((time.time() - start_time)))
    print('--- {0:.1f}% cells opened ---'.format(g.percentage_done() * 100))
    print('--- {0} (non-trivial) actions done ---'.format((steps_done)))
    print('--- seed: {} --- '.format(seed))