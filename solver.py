import argparse
import time
import logging
import numpy as np

from minesweeper import Minesweeper
from solver_clingo import ClingoSolver


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
    np.random.seed(seed)

    g = Minesweeper(args.width, args.height, args.bombs)
    if g.open(4,4):
        exit()

    if args.solver == 'clingo':
        s = ClingoSolver(g)
    elif args.solver == 'clingo-grouped':
        assert False, 'not implemented yet'
    else:
        assert False, 'not implemented yet'
        

    start_time = time.time()

    while True:
        best_action = s.solve_step()
        
        print('=== OPENING ', best_action)

        if g.open(*best_action):
            print(' === GAME OVER === ')
            break
        print(g)

        print('Trying trivial opening')
        s.find_trivial()

        if g.is_done():
            print(' === WON === ')
            print(g)
            break

        # os.system('clear')

        if args.interactive:
            input('Press a key to perform next action...')
        elif args.delay is not None:
            time.sleep(args.delay / 1000)

    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- seed: ", seed)