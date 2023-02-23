import argparse
import time
import random
import logging
import numpy as np

from minesweeper import Minesweeper
from solver_clingo import ClingoSolver
from solver_clingo_grouped import ClingoSolverGrouped


if __name__ == '__main__':
    # logging stuff
    logging.basicConfig()
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(fmt=' %(name)s :: %(levelname)-8s :: %(message)s'))
    logging.getLogger().addHandler(ch)

    # parsing arguments
    parser = argparse.ArgumentParser(prog='solver-clingo', description='Solves a randomly generated minesweeper instance using Clingo')
    parser.add_argument('--solver', choices=['clingo', 'clingo-grouped'], const='clingo', default='clingo', nargs='?', help='The solving approach to use')
    parser.add_argument('--no-trivial', help='If set, do not perform trivial cell opening/marking', action='store_true')
    parser.add_argument('-w', '--width', help='The width of the minesweeper instance', type=int, default=30) 
    parser.add_argument('-he', '--height', help='The height of the minesweeper instance', type=int, default=16) 
    parser.add_argument('-b', '--bombs', help='The number of bombs of the minesweeper instance', type=int, default=99) 
    parser.add_argument('-s', '--seed', help='Fixes the seed to generate the random minesweeper instance', type=int) 
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

    if args.solver == 'clingo':
        s = ClingoSolver(g)
    elif args.solver == 'clingo-grouped':
        s = ClingoSolverGrouped(g)
    else:
        assert False, 'not implemented yet'
        

    start_time = time.time()
    steps_done = 1

    while True:
        best_action = s.solve_step()
        
        print('=== OPENING ', best_action)

        if g.open(*best_action):
            print(' === GAME OVER === ')
            break
        
        steps_done += 1

        if not args.no_trivial:
            print('Trivials')
            g.open_trivials()

        if g.is_done():
            print(' === WON === ')
            print(g)
            break

        # os.system('clear')
        print(g)

        if args.interactive:
            input('Press a key to perform next action...')
        elif args.delay is not None:
            time.sleep(args.delay / 1000)

    if not args.interactive:
        print('--- {0:.2f} seconds ---'.format((time.time() - start_time)))
    print('--- {0} (non-trivial) actions done ---'.format((steps_done)))
    print('--- seed: {} --- '.format(seed))