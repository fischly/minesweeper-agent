import logging
import time
import os
import argparse

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
        self.ctl.load('clingo-programs/v4.lp') # load the solver program
        self.ctl.add(f'width({self.game.width}).\nheight({self.game.height}).\nnumberOfBombs({self.game.mines}).')


    def solve_step(self):
        self.reset()
        
        visible_field = self.game.get_visible_field()

        for x in range(self.game.width):
            for y in range(self.game.height):
                cell = visible_field[x, y]

                if cell == -2:
                    continue
                
                # if it is a marked bomb, add this as fact to our assumptions
                if cell == -3:
                    # self.ctl.add(f'bomb({x + 1}, {y + 1}).')
                    pass
                else:
                    self.ctl.add(f'number({x + 1}, {y + 1}, {int(cell)}).')
        
        self.ctl.ground()

        actions = {}
        bombs = {}
        model_count = 0

        with self.ctl.solve(yield_=True) as hnd:
            for m in hnd:
                symbols = m.symbols(shown=True)

                for symbol in symbols:
                    if symbol.name == 'open':
                        action = (symbol.arguments[0].number, symbol.arguments[1].number)

                        if not action in actions:
                            actions[action] = 1
                        else:
                            actions[action] += 1
                    
                    if symbol.name == 'bomb':
                        bomb = (symbol.arguments[0].number, symbol.arguments[1].number)

                        if not bomb in bombs:
                            bombs[bomb] = 1
                        else:
                            bombs[bomb] += 1

                model_count += 1
        
        proofen_bombs = filter(lambda b: bombs[b] == model_count, bombs)
        for proofen_bomb in proofen_bombs:
            self.game.mark(proofen_bomb[0] - 1, proofen_bomb[1] - 1)

        # select action that occured most often in the answer set
        # at best, it is one that occured in ALL the answer sets, which would make this action 100% safe
        best_action = max(actions, key=actions.get)

        # return the best action adjusted for a coordinate system that starts with 0 (the clingo implementation starts at 1)
        return (best_action[0] - 1, best_action[1] - 1)