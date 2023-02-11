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

    def open(self, x, y):
        """
        Opens a cell. If it has no bomb around, also opens all surrounding cells.
        Returns True is a bomb was hit, otherwhise false.
        """
        if self.field is None:
            self.field = self.generate_field((x, y))

        if self.explored[x, y]:
            return False
        
        self.explored[x, y] = 1

        if self.field[x, y] == -1:
            return True

        if self.field[x, y] == 0:
            for nx, ny in self._get_neighbours(x, y):
                self.open(nx, ny)


    def mark(self, x, y):
        """Mark a cell as bomb."""
        self.marked[x, y] = 1


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
        if start_position:
            # number of bombs inside the starting neighbourhood
            bombs = int(abs(np.sum(field[start_position[0] - 1:start_position[0]+2, start_position[1]-1:start_position[1]+2])))
            # clear the starting neighbourhood
            field[start_position[0] - 1:start_position[0]+2, start_position[1]-1:start_position[1]+2] = 0

            # reintroduce the deleted bombs on new (not yet occupied) positions (not in the starting neighbourhood)
            for _ in range(bombs):
                while True:
                    new_x = np.random.choice([n for n in range(self.width) if n not in range(start_position[0], start_position[0] + 2)])
                    new_y = np.random.choice([n for n in range(self.height) if n not in range(start_position[1], start_position[1] + 2)])

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
        """Returns only the field that is currently visible. Unknown fields contain the value -2."""
        # if a cell is not explored yet, return -2, also return the actual cell value
        visible = np.where(self.explored == 1, self.field, -2)
        flagged = np.where(self.marked == 1, -3, visible)

        return flagged
                

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