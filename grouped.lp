
%*
  expected input:
    - bomb(X, Y) for cells at position (X, Y) containing a bomb
    - number(X, Y, N) for cell at positin (X, Y) containing the number N
    - asked(X, Y) for cells that are unknown and the solver should find a possible assignment

*% 

-bomb(X, Y) :- number(X, Y, _).


% bomb(NX, NY) | -bomb(NX, NY) :- number(X, Y, _), neighbours(X, Y, NX, NY), not number(NX, NY, _). 
bomb(X, Y) | -bomb(X, Y) :- asked(X, Y).

neighbours(X, Y, NX, NY) :- 
  number(X, Y, _), 
  DX = -1..1, DY = -1..1, |DX|+|DY| > 0,
  NX = X + DX, NY = Y + DY, 
  NX >= 1, NX <= W, NY >= 1, NY <= H, % check if in bounds
  width(W), height(H).

neighbours(X, Y, NX, NY) :- 
  asked(X, Y), 
  DX = -1..1, DY = -1..1, |DX|+|DY| > 0,
  NX = X + DX, NY = Y + DY, 
  NX >= 1, NX <= W, NY >= 1, NY <= H,
  width(W), height(H).

% make sure the number of bombs does not exceed the maximum number
% :- numberOfBombs(NB), #count{ 1,X,Y : bomb(X, Y) } > NB.

% each number has to have exactly N bombs around it
:- asked(AX, AY), number(X, Y, N), neighbours(AX, AY, X, Y), #count{ 1,NX,NY : neighbours(X, Y, NX, NY), bomb(NX, NY) } != N.

open(X, Y) :- -bomb(X, Y), asked(X, Y).

#show open/2.
#show bomb/2.