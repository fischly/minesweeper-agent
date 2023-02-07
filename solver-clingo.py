import logging
import time
import os

from clingo.symbol import Number, Function
from clingo.control import Control

from minesweeper import Minesweeper

class ClingoSolver:

    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.ctl = Control()
        self.ctl.configuration.solve.models = 0 # return all models
        self.ctl.load('v3.lp') # load the solver program
        self.ctl.add(f'width({self.game.width}).\nheight({self.game.height}).\nnumberOfBombs({self.game.mines}).')

    def solve_step(self):
        self.reset()
        
        visible_field = self.game.get_visible_field()

        for x in range(self.game.width):
            for y in range(self.game.height):
                cell = visible_field[x, y]

                if cell >= 0:
                    self.ctl.add(f'number({x + 1}, {y + 1}, {int(cell)}).')
        
        self.ctl.ground()

        actions = {}
        model_count = 0

        with self.ctl.solve(yield_=True) as hnd:
            for m in hnd:
                # print(m)
                symbols = m.symbols(shown=True)

                for symbol in symbols:
                    if symbol.name == 'open':
                        action = (symbol.arguments[0].number, symbol.arguments[1].number)

                        if not action in actions:
                            actions[action] = 1
                        else:
                            actions[action] += 1

                model_count += 1
        
        logging.debug('ACTIONS:', actions)

        # select action that occured most often in the answer set
        # at best, it is one that occured in ALL the answer sets, which would make this action 100% safe
        best_action = max(actions, key=actions.get)

        logging.info(f'Selected best action {best_action} which occured in {actions[best_action]} of {model_count} answer sets ({(actions[best_action] / model_count)*100}%).')

        return best_action

    def _get_action_probabilities(self, models):
        pass

if __name__ == '__main__':
    # logging stuff
    logging.basicConfig()
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(fmt=' %(name)s :: %(levelname)-8s :: %(message)s'))
    logging.getLogger().addHandler(ch)

    # fix random seed
    import numpy as np
    np.random.seed(1)

    g = Minesweeper(30, 16, 99)
    if g.open(4,4):
        exit()

    print('GAME:')
    print(g)

    s = ClingoSolver(g)

    start_time = time.time()

    while True:
        best_action = s.solve_step()
        
        print('=== OPENING ', best_action)

        if g.open(best_action[0] - 1, best_action[1] - 1):
            print(' === GAME OVER === ')
            break

        if g.is_done():
            print(' === WON === ')
            break

        # os.system('clear')
        print(g)

        import time

        # time.sleep(1)

    print("--- %s seconds ---" % (time.time() - start_time))
    
