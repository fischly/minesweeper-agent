%*
As input, specify the facts as follow:

- width(W): the width of the playing field.
- height(H): the height of the playing field.
- numberOfBombs(NB): the total number of bombs.

- number(X, Y, N) for every number N with coordinates (X, Y) on the field.
- bomb(X, Y) for every bomb at position (X, Y).

Results in open(X, Y) atoms, which stand for cells that can safely be opened in the current answer set.

Multiple answer sets get generated for scenarios of uncertainty.
Consider the following 2x2 minesweeper field, where only the cell (1, 1) is known:

+---+
|1  |
|   |
+---+

In this case, three answer sets would be generated, placing the bomb at (1, 2), (2, 1) or (2, 2), respectively.

Note:
  For performance reasons, the solver considers only cells that are neighbouring at least one known number.
  Otherwhise, due to exponential complexity, grouding and search would quickly become infeasible for somewhat bigger fields.
*%


% if a cell is known to be a number, it cannot be a bomb
-bomb(X, Y) :- number(X, Y, _).

% otherwhise, neighbours of a known number that are not itself already known, can either be a bomb or not a bomb 
bomb(NX, NY) | -bomb(NX, NY) :- number(X, Y, _), neighbours(X, Y, NX, NY), not number(NX, NY, _). 

% utility function to get the 8 neighbours of a given cell
neighbours(X, Y, NX, NY) :- 
  number(X, Y, _), 
  DX = -1..1, DY = -1..1, |DX|+|DY| > 0,
  NX = X + DX, NY = Y + DY, 
  NX >= 1, NX <= W, NY >= 1, NY <= H, % check if in bounds
  width(W), height(H).

% remove answer sets, where the number of bombs exceeds the maximum number of allowed bombs
% Note: the stricter requirement of forcing the number of bombs to be the given amount
%       does not work due to the fact, that we only consider cells that have a known neighbour. 
:- numberOfBombs(NB), #count{ 1,X,Y : bomb(X, Y) } > NB.

% each number has to have exactly N bombs around it
:- number(X, Y, N), #count{ 1,NX,NY : neighbours(X, Y, NX, NY), bomb(NX, NY) } != N.

% output formatting: a cell can be opened if it is not a bomb and not a known number (specified in the input)
open(X, Y) :- -bomb(X, Y), not number(X, Y, _).

#show open/2.
#show bomb/2.