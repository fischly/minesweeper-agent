import random
import numpy as np

class Minesweeper:
    """A minesweeper game instance."""

    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines

        self.field = None  # load the field on first opening, so we can ensure that the first cell is not a bomb
        self.explored = np.zeros((width, height))
        self.marked = np.zeros((width, height))

        assert mines < width * height, 'cannot set more mines than number of cells in total'

        self.open_counter = 0
        self.trivial_counter = 0

    def open(self, x, y):
        """
            Opens a cell. If it has no bomb around, also opens all surrounding cells.
            Returns True is a bomb was hit, otherwhise false.
        """
        # if this is the first time opening a cell, generate the random field first
        if self.field is None:
            self.field = self.generate_field((x, y))

        # if cell is already explored, ignore this call
        if self.explored[x, y]:
            return False
        
        # otherwise, mark cell as explored
        self.explored[x, y] = 1
        self.open_counter += 1

        if self.field[x, y] == -1:
            return True

        # if opening a 0, open up all neighbours automatically
        if self.field[x, y] == 0:
            for nx, ny in self._get_neighbours(x, y):
                self.open(nx, ny)


    def mark(self, x, y):
        """Mark a cell as bomb."""
        self.marked[x, y] = 1

    def is_marked(self, x, y):
        """Returns True if this cell is marked, otherwise False."""
        return self.marked[x, y] == 1
    
    def is_open(self, x, y):
        """Returns whether the given cell is opened (either opened or marked)."""
        return self.marked[x, y] == 1 or self.explored[x, y] == 1

    def is_closed(self, x, y):
        """Returns whether the given cell is closed (not opened and not marked)."""
        return not self.is_open(x, y)

    def is_done(self):
        """Returns True if all non-mined fields have been opened."""
        # if the sum of the number of explored field plus the number of mines is equal to the number
        # of total cells, the game is finished
        return np.sum(np.where(self.field == -1, 1, self.explored)) == self.width * self.height

    def percentage_done(self):
        """Returns the percentage of how much of the field has been opened yet."""
        return np.sum(self.explored) / (self.width * self.height - self.mines)

    def generate_field(self, start_position=None):
        """Generate a new field by placing the mines randomly."""
        # create a 1d array with exactly (number of mines) -1's and the rest filled with zeros         
        field = np.concatenate([np.ones(self.mines) * -1, np.zeros(self.width * self.height - self.mines)])

        # shuffle the 1d array to get a random mine placement
        np.random.shuffle(field)

        # reshape to 2d array to represent the field
        field = field.reshape((self.width, self.height))

        # make sure we do not have any bombs at the start position and its surrounding
        if start_position and (self.width * self.height) - 9 >= self.mines:
            # number of bombs inside the starting neighbourhood
            bombs = int(abs(np.sum(field[start_position[0] - 1:start_position[0]+2, start_position[1]-1:start_position[1]+2])))
            # clear the starting neighbourhood
            field[start_position[0] - 1:start_position[0]+2, start_position[1]-1:start_position[1]+2] = 0

            # reintroduce the deleted bombs on new (not yet occupied) positions (not in the starting neighbourhood)
            for _ in range(bombs):
                while True:
                    new_x = np.random.choice([n for n in range(self.width)])
                    new_y = np.random.choice([n for n in range(self.height)])

                    if new_x in range(start_position[0] - 1, start_position[0] + 2) and \
                       new_y in range(start_position[1] - 1, start_position[1] + 2):
                       continue

                    if field[new_x, new_y] != -1:
                        break
                field[new_x, new_y] = -1

        # calculate numbers
        for x in range(self.width):
            for y in range(self.height):
                if field[x, y] != -1:
                    field[x, y] = self._calculate_number_of_bombs(field, x, y)
        
        return field


    def get_visible_field(self):
        """
            Returns only the field that is currently visible.
            Unknown fields contain the value -2, marked cell contain the value -3.
        """
        visible = np.where(self.explored == 1, self.field, -2)
        flagged = np.where(self.marked == 1, -3, visible)

        return flagged

    def open_trivials(self):
        """
            Handels the trivial cases that can easily be solved algorithmically:
             - Looks for number-cells that are already satisfied, in which case it opens all unexplored neighbors.
             - Looks for number-cells where the number of marked bombs plus the number of unknowns sum up to the cell value, 
                marking the unknowns as bombs.
        """
        visible_field = self.get_visible_field()

        did_change = False

        # check each cell
        for x in range(self.width):
            for y in range(self.height):
                cell = visible_field[x, y]

                # ignore flagged or unknown
                if cell == -3 or cell == -2 or cell == -1:
                    continue

                # count neighbouring bomb/unknown cells
                number_of_bombs = 0
                number_of_unknowns = 0

                neighbours = list(self._get_neighbours(x, y))
                
                for nx, ny in neighbours:
                    if visible_field[nx, ny] == -3 or visible_field[nx, ny] == -1:
                        number_of_bombs += 1
                    if visible_field[nx, ny] == -2:
                        number_of_unknowns += 1
                
                # (1) check if number is satisfied, in which case we open it's neighbours
                if number_of_bombs >= cell:
                    for nx, ny in neighbours:
                        if visible_field[nx, ny] == -2:
                            self.open(nx, ny)
                            did_change = True

                # (2) check if a number's neighbours can only be mines, in which case we mark it as mines
                if cell >= number_of_unknowns + number_of_bombs:
                    for nx, ny in neighbours:
                        if visible_field[nx, ny] == -2:
                            self.mark(nx, ny)
                            did_change = True

        if did_change:
            self.open_trivials()
        
                

    def _calculate_number_of_bombs(self, field, x, y):
        """Helper function to calculate the number of surrounding bombs."""
        num = 0

        for nx, ny in self._get_neighbours(x, y):
            if field[nx, ny] == -1:
                num += 1

        return num 

    
    def _get_neighbours(self, x, y):
        """Returns all neighbouring cell's coordinates of the given cell."""

        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                # skip the center cell
                if nx == x and ny == y:
                    continue
                
                # skip cells out of bound
                if nx < 0 or nx >= self.width or \
                   ny < 0 or ny >= self.height:
                   continue

                yield (nx, ny)

    def _get_closed_neighbours(self, x, y):
        """Returns all closed (not opened or marked) neighbouring cell's coordinates of the given cell."""
        neighbours = self._get_neighbours(x, y)
        
        return filter(lambda nb: self.is_closed(*nb), neighbours)

    def __str__(self):
        visible = self.get_visible_field().T

        # convert to chars
        c = np.char.mod('%i', visible)
        c[c == '-2'] = ' '
        c[c == '-1'] = 'B'
        c[c == '-3'] = '\u2691'

        percentage = str(int(self.percentage_done() * 100 + 0.5)) + '%'

        result = '+-' + '-' * (self.width * 2 - 1) + '-+\n'
        result += '| Done: ' + percentage + ' ' * (self.width * 2 - 7 - len(percentage)) + ' |\n'
        result += '|-' + '-' * (self.width * 2 - 1) + '-|\n'

        for row in range(c.shape[0]):
            result += '| ' + ' '.join(c[row]) + ' |\n'

        result += '+-' + '-' * (self.width * 2 - 1) +  '-+'

        return result

    def __repr__(self):
        return str(self)