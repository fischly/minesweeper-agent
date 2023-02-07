

% if there is a number given as fact, then there cannot be a bomb on that field
-bomb(X, Y) :- number(X, Y, _).

% a field consists of w x h cells 
cell(X, Y) :- width(W), height(H), X = 1..W, Y = 1..H.

% each field can either be a bomb or not a bomb
bomb(X, Y) | -bomb(X, Y) :- cell(X, Y).

% every field that is not a bomb consists of a number, which is exactly the number of neighbouring bombs
number(X, Y, N) :- -bomb(X, Y), N = #count{ 1,NX,NY : neighbours(X, Y, NX, NY), bomb(NX, NY) }.

% gets all (valid) neighbouring cells
neighbours(X, Y, X + DX, Y + DY) :- 
  cell(X, Y), 
  DX = -1..1, DY = -1..1, |DX|+|DY| > 0,
  cell(X + DX, Y + DY). % check if in bounds


% fix number of bombs
:- numberOfBombs(NB), #count{ 1,X,Y : bomb(X, Y) } != NB.

% each number has to have exactly N bombs around it
:- number(X, Y, N), #count{ 1,NX,NY : neighbours(X, Y, NX, NY), bomb(NX, NY) } != N.

#show -bomb/2.