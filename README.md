# functionaltree #

[![build status](https://square-src.de/ci/projects/2/status.png?ref=master)](https://square-src.de/ci/projects/2?ref=master)

A educational Binary Search Tree (BST) (visualization) framework.


## BST Implementations ##

- unbalanced BST (`naive.py`)
- Red-Black Trees (`rb.py`)
- Splay Trees (`splay.py`)

## Visualization ##

See `treeview.py` for an example.


## Requirements ##
`python3`

The old viewer in `drawing.py` needs

- `matplotlib` and
- `networkx`

which can be installed with `pip`.

The new viewer just needs `tkinter` which should be in the standard library.
You maybe have to do 
```sh
sudo apt-get install python3-tk
```
