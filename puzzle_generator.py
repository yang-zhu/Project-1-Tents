import sys
from tents_formula_v2 import GridWithTents, solveGrid
from random import randrange, choice


def generateGrid(height, width):
    grid = GridWithTents(height, width)
    
    loop_count = 0 
    while True:
        # count how many times the while-loop is executed without adding new trees
        loop_count += 1
        if loop_count > 50000:
            break
        
        tree = (randrange(height), randrange(width))
        tents = grid.treeNeighbors(*tree)
        if tents != []:
            if grid.addTreeTent(tree, choice(tents)):
                loop_count = 0
    return grid


if len(sys.argv) != 4:
    print('Please input four arguments: <path of the CaDiCal prorgam> <number of rows> <number of columns>')
    exit(1)

height = int(sys.argv[2])
width = int(sys.argv[3])
grid = generateGrid(height, width)

solution = solveGrid(sys.argv[1], grid.withoutTents(), grid.tents())

while solution != None:
    for t in set(t for t in grid.tents() if t not in solution):
        if randrange(2) != 0:
            continue
        grid.delTreeTent(t)
    solution = solveGrid(sys.argv[1], grid.withoutTents(), grid.tents())

grid.printPuzzle()

print()
grid.printSolution(grid.tents())
