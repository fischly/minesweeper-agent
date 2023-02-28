import logging
import time
import os

from clingo.symbol import Number, Function
from clingo.control import Control

from minesweeper import Minesweeper

class ClingoSolverGrouped:

    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.ctl = Control()
        self.ctl.configuration.solve.models = 0 # return all models
        self.ctl.load('clingo-programs/grouped.lp') # load the solver program
        self.ctl.add(f'width({self.game.width}).\nheight({self.game.height}).\nnumberOfBombs({self.game.mines}).')

    def solve_step(self):
        best_actions = self.solve_groups()
        best_action = max(best_actions, key=lambda a: a[1])[0]

        return (best_action[0] - 1, best_action[1] - 1)

    def solve_groups(self):
        actions = []

        # get groups
        groups = self.find_unopened_groups()

        for group in groups:
            group_asked = []
            for cell in group:
                group_asked += self.game._get_closed_neighbours(*cell)

            group_asked = list(set(group_asked))

            best_group_action = self.solve_group(group_asked)
            if best_group_action is not None:
                actions.append(best_group_action)

        return actions

    def solve_group(self, asked_for):
        self.reset()
        
        visible_field = self.game.get_visible_field()

        for x in range(self.game.width):
            for y in range(self.game.height):
                cell = visible_field[x, y]

                if cell == -2:
                    continue
                
                # if it is a marked bomb, add this as fact to our assumptions
                if cell == -3:
                    self.ctl.add(f'bomb({x + 1}, {y + 1}).')
                else:
                    self.ctl.add(f'number({x + 1}, {y + 1}, {int(cell)}).')

        for asked_x, asked_y in asked_for:
            self.ctl.add(f'asked({asked_x + 1}, {asked_y + 1}).')

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

        if len(actions) == 0:
            return 

        # select action that occured most often in the answer set
        # at best, it is one that occured in ALL the answer sets, which would make this action 100% safe
        best_action = max(actions, key=actions.get)

        return best_action, actions[best_action] / model_count

    def find_unopened_groups(self):
        visible_field = self.game.get_visible_field()
        
        seen = set()

        def is_open(cell):
                cv = visible_field[cell[0], cell[1]]
                return cv != -2 or self.game.marked[cell[0], cell[1]] == 1
        def is_closed(cell):
            return not is_open(cell)

        def hasCommonClosedNeighbour(cell1, cell2):    
            neighbours1 = set(filter(is_closed, self.game._get_neighbours(cell1[0], cell1[1])))
            neighbours2 = set(filter(is_closed, self.game._get_neighbours(cell2[0], cell2[1])))

            intersection = neighbours1.intersection(neighbours2)

            return len(intersection) > 0

        def hasClosedNeighbours(cell):
            return len(list(filter(is_closed, self.game._get_neighbours(cell[0], cell[1])))) > 0

        def group(cell, current_group, last_cell):
            cv = visible_field[cell[0], cell[1]]

            if cv == -2:
                for neighbour in self.game._get_neighbours(cell[0], cell[1]):
                    
                    if not (self.game.is_closed(*cell) and self.game.is_closed(*neighbour)):
                        group(neighbour, current_group, cell)
            else:
                # ignore cells without unknown neighbours, since they won't contribute to the search in any way
                if not hasClosedNeighbours(cell):
                    return

                # ignore cells that do not have any mines as neighbours (which again wont contribute to search)
                # ignore cells that have been already visited as a stop condition for the recursion
                # ignore cells that have been marked (which in our case means, that the AI is sure there is a mine)
                if cv == 0 or cell in seen or self.game.marked[cell[0], cell[1]] == 1:
                    return
                
                # also stop, if this has been a recursive call (last_cell != None) but there are no common closed 
                # neighbours between the last_cell and the current cell (which means they should NOT be in the same group)
                if last_cell is not None and visible_field[last_cell[0], last_cell[1]] != -2 and not hasCommonClosedNeighbour(cell, last_cell):
                    return

                # so if current is not unknown (we do not want unknowns in the group) and current and last cells have at least 
                # one common closed neighbour, we can expand the current group with the current cell and mark the current cell as seen
                current_group.append(cell)
                seen.add(cell)

                # recursively try to add all neighbours of the current cell to the current group
                for neighbour in self.game._get_neighbours(cell[0], cell[1]):
                    
                    group(neighbour, current_group, cell)

        
        groups = []
        # iterate over all cells and try to add them to a new group. during the group() call, the group will expand to 
        # include all the cells that have at least one common closed neighbour with the starting cell
        for x in range(self.game.width):
            for y in range(self.game.height):
                grp = []
                group((x, y), grp, None)

                if len(grp) > 0:
                    groups.append(grp)

        return groups
