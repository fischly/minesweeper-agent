import logging
import time

import numpy as np
import cpmpy

from minesweeper import Minesweeper

class CSPSolverGrouped:
    def __init__(self, game):
        self.game = game

    def solve_step(self):
        best_actions = self.solve_groups()
        best_action = min(best_actions, key=lambda a: a[1])[0]

        return best_action

    def solve_groups(self):
        actions = []

        # get groups
        groups = self.find_unopened_groups()

        for group in groups:
            group_asked = []

            for cell in group:
                group_asked += self.game._get_closed_neighbours(*cell)

            group_asked = list(set(group_asked))

            best_group_action = self.solve_group(group_asked, group)
            if best_group_action is not None:
                actions.append(best_group_action)

        return actions


    def solve_group(self, asked_for, knowns):
        visible_field = self.game.get_visible_field()

        # the model and variables the solver should assign
        model = cpmpy.Model()

        variables = {}
        self.bomb_count = {}
        self.model_counter = 0
        
        for x, y in asked_for:
            variables[(x, y)] = cpmpy.boolvar()
            self.bomb_count[(x, y)] = 0

        for x, y in knowns:
            model += (sum(variables[(nx, ny)] for nx, ny in self.game._get_neighbours(x, y) if (nx, ny) in variables) + \
                     (sum(1 for nx, ny in self.game._get_neighbours(x, y) if visible_field[nx, ny] == -3)) \
                       == int(visible_field[x, y]))


        # callback for a found model
        def handle_result():
            for x, y in variables.keys():
                if variables[(x, y)].value():
                    self.bomb_count[(x, y)] += 1 

            self.model_counter += 1

        # ask the solver to provide all models
        models = model.solveAll(display=handle_result)

        if self.model_counter <= 0:
            return

        safest_cell = min(self.bomb_count, key=self.bomb_count.get)
        safest_cell_occ = self.bomb_count[safest_cell]

        return safest_cell, safest_cell_occ / self.model_counter


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
                # if not (self.game.is_closed(*cell) and self.game.is_closed(*last))
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