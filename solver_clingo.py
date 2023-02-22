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
        self.ctl.load('v4.lp') # load the solver program
        self.ctl.add(f'width({self.game.width}).\nheight({self.game.height}).\nnumberOfBombs({self.game.mines}).')

    def find_trivial(self):
        visible_field = self.game.get_visible_field()

        for x in range(self.game.width):
            for y in range(self.game.height):
                cell = visible_field[x, y]

                # flagged or unknown
                if cell == -3 or cell == -2 or cell == -1:
                    continue

                number_of_bombs = 0
                number_of_unknowns = 0

                neighbours = list(self.game._get_neighbours(x, y))
                
                for nx, ny in neighbours:
                    if visible_field[nx, ny] == -3 or visible_field[nx, ny] == -1:
                        number_of_bombs += 1
                    if visible_field[nx, ny] == -2:
                        number_of_unknowns += 1
                
                # (1) check if number is satisfied, in which case we open it's neighbours
                if number_of_bombs >= cell:
                    for nx, ny in neighbours:
                        if visible_field[nx, ny] == -2:
                            self.game.open(nx, ny)

                # (2) check if a number's neighbours can only be mines, in which case we mark it as mines
                if cell >= number_of_unknowns + number_of_bombs:
                    for nx, ny in neighbours:
                        if visible_field[nx, ny] == -2:
                            self.game.mark(nx, ny)


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
                    #print(f'bomb({x + 1}, {y + 1}).')
                    # self.ctl.add(f'bomb({x + 1}, {y + 1}).')
                    pass
                else:
                    #print(f'number({x + 1}, {y + 1}, {cell}).')
                    self.ctl.add(f'number({x + 1}, {y + 1}, {int(cell)}).')
        
        self.ctl.ground()

        actions = {}
        bombs = {}
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
                    
                    if symbol.name == 'bomb':
                        bomb = (symbol.arguments[0].number, symbol.arguments[1].number)

                        if not bomb in bombs:
                            bombs[bomb] = 1
                        else:
                            bombs[bomb] += 1

                model_count += 1
        
        logging.debug('ACTIONS:', actions)
        # logging.debug('BOMBS: ', bombs)

        proofen_bombs = filter(lambda b: bombs[b] == model_count, bombs)
        for proofen_bomb in proofen_bombs:
            self.game.mark(proofen_bomb[0] - 1, proofen_bomb[1] - 1)

        # select action that occured most often in the answer set
        # at best, it is one that occured in ALL the answer sets, which would make this action 100% safe
        best_action = max(actions, key=actions.get)

        logging.info(f'Selected best action {best_action} which occured in {actions[best_action]} of {model_count} answer sets ({(actions[best_action] / model_count)*100}%).')

        # return the best action adjusted for a coordinate system that starts with 0 (the clingo implementation starts at 1)
        return (best_action[0] - 1, best_action[1] - 1)