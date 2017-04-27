# charnet - characters network

This project aims to perform complex network studies in 9 books using
 characters as nodes and characters encounters as edges. The project
 has a [GitHub page](https://ajholanda.github.io/charnet/) and a
 [manuscript](https://arxiv.org/abs/1704.08197).

## Directories content

* `data` - data gathered for the project;
* `sgb` - some data from [Stanford GraphBase](http://www-cs-faculty.stanford.edu/~uno/sgb.html).

## Prerequisites

* Python and the packages:
  ** [matplotlib](https://matplotlib.org/);
  ** [NetworkX](https://networkx.github.io/);
  ** [PyGraphviz](https://pygraphviz.github.io/).

## Running

To generate all results and plots, just run:

````
$ make
````

To select a specific target, see the help:

````
$ make help
````

To clean the output generated:

````
$ make clean
````
