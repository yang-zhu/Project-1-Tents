import sys
from encoding import GridWithTents, solveGrid
from random import randrange, choice


def fillGrid(grid):
    loop_count = 0 
    while True:
        # count how many times the while-loop is executed without adding new trees
        loop_count += 1
        if loop_count > 2000:
            break
        
        tree = (randrange(grid.height), randrange(grid.width))
        tents = grid.treeNeighbors(*tree)
        if tents != []:
            if grid.addTreeTent(tree, choice(tents)):
                loop_count = 0


if len(sys.argv) != 4:
    print('Please input four arguments: <path of the CaDiCal prorgam> <number of rows> <number of columns>')
    exit(1)

height = int(sys.argv[2])
width = int(sys.argv[3])
grid = GridWithTents(height, width)
fillGrid(grid)

solution = solveGrid(sys.argv[1], grid.withoutTents(), grid.tents())

while solution != None:
    for t in set(t for t in grid.tents() if t not in solution):
        grid.delTreeTent(t)
    fillGrid(grid)
    solution = solveGrid(sys.argv[1], grid.withoutTents(), grid.tents())

grid.printPuzzle()
