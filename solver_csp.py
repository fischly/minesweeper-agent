import logging
import time

import numpy as np
import cpmpy

from minesweeper import Minesweeper

class CSPSolver:
    def __init__(self, game):
        self.game = game
        

    def solve_step(self):
        visible_field = self.game.get_visible_field()

        # the model and variables the solver should assign
        model = cpmpy.Model()
        mines = cpmpy.boolvar(shape=visible_field.shape) # 2d boolean variable array, saying if cell (x, y) contains a mine

        for x in range(self.game.width):
            for y in range(self.game.height):
                cell = visible_field[x, y]

                # cell has been marked as a bomb previously, so provide this as a fact to the solver
                if cell == -3:
                    model += mines[x, y] == 1

                # cell is a number, which means we want to add the constraint, that the sum of neighbouring mines should be equal to the number value
                if cell >= 0:
                    model += mines[x, y] == 0  # cell is a number, so it cannot be a mine
                    model += sum(mines[nx, ny] for nx, ny in self.game._get_neighbours(x, y)) == int(visible_field[x, y])        

        # helper variable to count how often a cell was set to a bomb over all models
        self.bomb_count = np.zeros(visible_field.shape)
        self.model_counter = 0

        # callback for a found model
        def handle_result():
            self.bomb_count += np.array(mines.value(), dtype=np.float64) # casting needed to convert Boolean variables to numbers for summation
            self.model_counter += 1

        # ask the solver to provide all models
        model.solveAll(display=handle_result)

        # go over each cell and check if it was set to a bomb in every model
        # if it was, we can safely mark it as bomb
        for x in range(self.game.width):
            for y in range(self.game.height):
                if self.bomb_count[x, y] >= self.model_counter:
                    self.game.mark(x, y)

        # set all cells with already known cells to inf
        filtered = np.where(visible_field >= 0, np.inf, self.bomb_count)
        # set all cells that resulted in NaN due to the solver not assigning a value since the cell had no constraint
        filtered = np.where(np.isnan(filtered), np.inf, filtered)
        # find out the cell index which contained least often a bomb over all models (most safe cell to open)
        safest_cell = np.unravel_index(np.argmin(filtered), visible_field.shape)
        
        return safest_cell
