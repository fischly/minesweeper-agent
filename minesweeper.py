import random
import numpy as np

class Minesweeper:
    """A minesweeper game instance."""
    
    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines

        self.field = self.generate_field()
        self.explored = np.full((width, height), 0)


    def open(self, x, y):
        """Opens a cell. If it has no bomb around, also opens all surrounding cells."""
        if self.explored[x, y]:
            return
        
        self.explored[x, y] = 1

        if self.field[x, y] == 0:
            for nx, ny in self._get_neighbours(x, y):
                self.open(nx, ny)


    def generate_field(self):
        """Generate a new field by placing the mines randomly."""
        # create a 1d array with exactly #mines -1's and the rest filled with zeros         
        field = np.concatenate([np.ones(self.mines) * -1, np.zeros(self.width * self.height - self.mines)])

        # shuffle the 1d array to get a random mine placement
        np.random.shuffle(field)

        # reshape to 2d array to represent the field
        field = field.reshape((self.width, self.height))

            

        # calculate numbers
        for x in range(self.width):
            for y in range(self.height):
                if field[x, y] != -1:
                    field[x, y] = self._calculate_number_of_bombs(field, x, y)
        
        return field


    def get_visible_field(self):
        """Returns only the field that is currently visible. Unknown fields contain the value -2."""
        # if a cell is not explored yet, return -2, also return the actual cell value
        return np.where(self.explored == 1, self.field, -2)
                

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

        result = '+' + '-' * (self.width * 2 - 1) + '+\n'
        
        for row in range(c.shape[0]):
            result += '|' + ' '.join(c[row]) + '|\n'

        result += '+' + '-' * (self.width * 2 - 1) +  '+'

        return result

    def __repr__(self):
        return str(self)