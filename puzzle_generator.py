import sys
from encoding import GridWithTents, solveGrid
from random import randrange, choice


def fillGrid(grid):
    '''Adds tree-tent pairs randomly to fill the grid.'''
    loop_count = 0 
    while True:
        # Count how many times the while-loop is executed without adding new trees.
        loop_count += 1
        if loop_count > 2000:
            break
        
        tree = (randrange(grid.height), randrange(grid.width))
        tents = grid.treeNeighbors(*tree)
        if tents != []:
            if grid.addTreeTent(tree, choice(tents)):
                loop_count = 0

# Output error message when the input is illegal.
if len(sys.argv) != 4:
    print('Please input four arguments: <path of the CaDiCaL prorgam> <number of rows> <number of columns>')
    exit(1)

# Create a grid filled with trees and tents.
height = int(sys.argv[2])
width = int(sys.argv[3])
grid = GridWithTents(height, width)
fillGrid(grid)

# Try to find a different solution by ruling out the generated one.
solution = solveGrid(sys.argv[1], grid.withoutTents(), excluded_sol=grid.tents())

# Keep adjusting the puzzle (remove and refill) until it has a unique solution.
while solution != None:
    # Remove the tree-tent pairs that differ from the excluded solution.
    for t in set(t for t in grid.tents() if t not in solution):
        grid.delTreeTent(t)
    # Refill the grid and retry.
    fillGrid(grid)
    solution = solveGrid(sys.argv[1], grid.withoutTents(), grid.tents())

# Print the puzzle on the terminal.
grid.printPuzzle()
