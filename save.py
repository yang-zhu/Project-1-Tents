import argparse
from tents_formula_v2 import solveGrid,gridInput


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GUI Solve & Save puzzles.")
    args = parser.parse_args()

    args.input_file='/Users/macair/Documents/GitHub/Project-1-Tents/test.txt'   
    args.cadical='/Users/macair/Documents/GitHub/Project-1-Tents/save.txt'


    grid = gridInput(args.input_file)
    solution = solveGrid(args.cadical, grid)

    # Prints the solution
    if solution == None:
        print('There is no solution to this puzzle, please re-enter')
    else:
        path = '/Users/macair/Documents/GitHub/Project-1-Tents/test.txt'
        f = open(path, 'a+')   
        for r in range(grid.height):
             for c in range(grid.width):
                 if (r, c) in solution:
                     f.write('Δ')
                 elif (r, c) in grid.trees:
                     f.write('T')
                 else:
                     f.write('.')
             f.write(str(grid.tents_in_row[r])+"\n")
        for num in grid.tents_in_col:
             f.write(str(num))





