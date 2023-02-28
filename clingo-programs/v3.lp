
% if there is a number given as fact, then there cannot be a bomb on that field
-bomb(X, Y) :- number(X, Y, _).

% a field consists of w x h cells 
cell(1..W, 1..H) :- width(W), height(H).

% each field can either be a bomb or not a bomb
bomb(NX, NY) | -bomb(NX, NY) :- number(X, Y, _), neighbours(X, Y, NX, NY), not number(NX, NY, _). 

% gets all (valid) neighbouring cells
neighbours(X, Y, X + DX, Y + DY) :- 
  cell(X, Y), 
  DX = -1..1, DY = -1..1, |DX|+|DY| > 0,
  cell(X + DX, Y + DY). % check if in bounds
  
% make sure the number of bombs does not exceed the maximum number
:- numberOfBombs(NB), #count{ 1,X,Y : bomb(X, Y) } > NB.

% each number has to have exactly N bombs around it
:- number(X, Y, N), #count{ 1,NX,NY : neighbours(X, Y, NX, NY), bomb(NX, NY) } != N.

open(X, Y) :- -bomb(X, Y), not number(X, Y, _).

#show open/2.
#show bomb/2.