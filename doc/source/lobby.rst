Lobby or h index
================

All graph vertices are traversed and Lobby index is calculated and stored in the lobby macro-field.

If a node has the following list of neighbors sorted by degree:

==========  ========
neighbor     degree
==========  ========
   1          21 
   2          18 
   3           4 
   4           3 
==========  ========
   
the Lobby index is 3 because degree $\leq$ neighbor_position. Degree repetitions are not accounted.

.. autofunction:: lobby
