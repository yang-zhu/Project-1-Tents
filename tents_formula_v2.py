import subprocess
import sys


class Grid:
    def __init__(self, height, width, trees, empty, tents_in_row, tents_in_col):
        assert height == len(tents_in_row), width == len(tents_in_col)
        self.height = height
        self.width = width
        self.trees = trees
        self.empty = empty
        self.tents_in_row = tents_in_row
        self.tents_in_col = tents_in_col
    
    def __str__(self):
        return str({'height': self.height,'width': self.width, 'trees': self.trees, 'tents in row': self.tents_in_row, 'tents in column': self.tents_in_col})

def gridInput(gridFile):
    '''Reads the grid input.'''
    with open(gridFile) as f:
        height, width = map(int, f.readline().split())
        trees = set()
        tents_in_row = []
        for lineIndex in range(height):
            (line, tentNum) = f.readline().split()
            tents_in_row.append(int(tentNum))
            for (cellIndex, cell) in enumerate(line):
                if cell == 'T':
                    trees.add((lineIndex, cellIndex))
        tents_in_col = [int(t) for t in f.readline().split()]
        empty = set((r, c) for r in range(height) for c in range(width) if (r, c) not in trees)
        return Grid(height, width, trees, empty, tents_in_row, tents_in_col)

def solveGrid(cadical_path, grid, excluded_sol = None):
    clauses = [] # Stores all the clauses
    varDict = {}  # Stores all the generated variables

    def generateVar(varDescr):
        '''Generates a variable from the variable description.'''
        if varDescr not in varDict:
            varDict[varDescr] = len(varDict) + 1
        return varDict[varDescr]

    def tentVar(r, c):
        '''Cell at (r, c) contains a tent.'''
        assert r < grid.height and c < grid.width
        assert (r, c) in grid.empty
        return generateVar(('tent', r, c))

    def arrowVar(r, c, r_tent, c_tent):
        '''There is an arrow pointing from each tree (r, c) to the tent it owns.'''
        assert r_tent in range(grid.height) and c_tent in range(grid.width)
        assert r in range(grid.height) and c in range(grid.width)
        return generateVar(('arrow', r, c, r_tent, c_tent))

    def countVar(count, start_row, start_col, end_row, end_col):
        '''The cells from (start_row, start_col) to (end_row, end_col) contain count many tents.'''
        return generateVar(('count', count, start_row, start_col, end_row, end_col))

    def boundFilter(lis, height, width):
        '''Filters out coordinates that are occupied by trees or out of bounds of a grid.'''
        return [(x, y) for (x, y) in lis if x >= 0 and x < height if y >= 0 and y < width if (x, y) not in grid.trees]

    def boundFilterTree(lis, height, width):
        '''Filters out coordinates that are not occupied by trees or out of bounds of a grid .'''
        return [(x, y) for (x, y) in lis if x >= 0 and x < height if y >= 0 and y < width if (x, y) in grid.trees]

    def noTentIndex(r, c):
        '''Neighboring cells of a cell with tent can't have tents.'''
        return boundFilter([(r_n, c_n) for r_n in [r-1, r, r+1] for c_n in [c-1, c, c+1] if not ((r_n == r) and (c_n == c))], grid.height, grid.width)


    # Rule out the given solution
    if excluded_sol != None:
        clauses.append(tuple(-tentVar(*cell) for cell in excluded_sol))
    

    # No two tents are adjacent in any of the (up to) 8 directions
    for (r1, c1) in grid.empty:
        for (r2, c2) in noTentIndex(r1, c1):
            clauses.append((-tentVar(r1, c1), -tentVar(r2, c2)))


    def pair_clause_helper(lis):
        '''Chooses 2 variables out of a list to build clauses.'''
        return [(ele1, ele2) for ele1 in lis for ele2 in lis if ele2 != ele1]

    # Every tree has exactly one arrow
    for (r, c) in grid.trees:
        neighbor_cells = boundFilter([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width)

        # Every arrow points to a tent
        clauses += [(-arrowVar(r, c, r1, c1), tentVar(r1, c1)) for (r1, c1) in neighbor_cells]
        
        # Every tree has at least one arrow
        clause = tuple(arrowVar(r, c, r1, c1) for (r1, c1) in neighbor_cells)   
        clauses.append(clause)    
        
        # Every tree has at most one arrow
        for ((r1, c1), (r2, c2)) in pair_clause_helper(neighbor_cells):
            clauses.append((-arrowVar(r, c, r1, c1), -arrowVar(r, c, r2, c2)))
        
    # There is exactly one arrow pointing to every tent
    for (r, c) in grid.empty:
        tree_cells = boundFilterTree([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width)
        
        # There is at least one arrow pointing to every tent
        clause = [-tentVar(r, c)]
        clause += [arrowVar(r1, c1, r, c) for (r1, c1) in tree_cells]
        clauses.append(tuple(clause))
        
        # There is at most one arrow pointing to every tent
        clauses += [(-arrowVar(r1, c1, r, c), -arrowVar(r2, c2, r, c)) for ((r1, c1), (r2, c2)) in pair_clause_helper(tree_cells)]


    def countTents(count, empty_cells):
        if count > len(empty_cells):
            return [(1,),(-1,)]
        clauses = []
        if count == 0:
            clauses += [(-tentVar(r, c),) for (r, c) in empty_cells]
        else:
            if len(empty_cells) > 1:
                clauses.append((-tentVar(*empty_cells[0]), countVar(count-1, *empty_cells[1], *empty_cells[-1])))
                clauses.append((tentVar(*empty_cells[0]), countVar(count, *empty_cells[1], *empty_cells[-1])))
                for i in range(1, len(empty_cells)):
                    for num in range(count+1):
                        if num < len(empty_cells) - i and num > 0:
                            clauses.append((-tentVar(*empty_cells[i]), -countVar(num, *empty_cells[i], *empty_cells[-1]), countVar(num-1, *empty_cells[i+1], *empty_cells[-1])))
                            clauses.append((tentVar(*empty_cells[i]), -countVar(num, *empty_cells[i], *empty_cells[-1]), countVar(num, *empty_cells[i+1], *empty_cells[-1])))
                        elif num == len(empty_cells) - i:
                            for j in range(i, len(empty_cells)):
                                clauses.append((-countVar(num, *empty_cells[i], *empty_cells[-1]), tentVar(*empty_cells[j])))
                        elif num == 0:
                            for j in range(i, len(empty_cells)):
                                clauses.append((-countVar(num, *empty_cells[i], *empty_cells[-1]), -tentVar(*empty_cells[j])))
            else:
                assert len(empty_cells) == count == 1
                clauses.append((tentVar(*empty_cells[0]),))

        return clauses

    # Every row has exactly the required number of tents
    for r in range(grid.height):
        count = grid.tents_in_row[r]
        clauses += countTents(count, [(r, c) for c in range(grid.width) if (r, c) not in grid.trees])

    # Every column has exactly the required number of tents
    for c in range(grid.width):
        count = grid.tents_in_col[c]
        clauses += countTents(count, [(r, c) for r in range(grid.height) if (r, c) not in grid.trees])


    # Output the clauses in DIMACS CNF format as a string
    res = 'p cnf ' + str(len(varDict)) + ' ' + str(len(clauses)) + '\n'
    res += '\n'.join([' '.join(map(str, clause)) + ' 0' for clause in clauses]) + '\n'

    print("running solver with", len(varDict), "variables and", len(clauses), "clauses...")

    # Feeds the cnf formula into CaDiCal
    solver_process = subprocess.Popen([cadical_path, '-q'], stdin = subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')

    (solution, _) = solver_process.communicate(input = res)

    positive = set()  # Stores all the positiv assignments, including the locations of tents
    for line in solution.split('\n'):
        if len(line) < 2:
            continue
        (x, *rest) = line.split()
        if x == 'v':
            for var in rest:
                if int(var) > 0:
                    positive.add(int(var))
        elif x == 's' and rest == ['UNSATISFIABLE']:
            return None
    
    tents = set((r, c) for (r, c) in grid.empty if tentVar(r, c) in positive)  # Stores all the cells with tents
    
    return tents


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Please input two arguments: <path of the CaDiCal prorgam> <path of the grid file>')
        exit(1)

    grid = gridInput(sys.argv[2])
    solution = solveGrid(sys.argv[1], grid)

    # Prints the solution
    if solution == None:
        print('UNSATISFIABLE')
    else:
        for r in range(grid.height):
            for c in range(grid.width):
                if (r, c) in solution:
                    print('Δ', end=' ')
                elif (r, c) in grid.trees:
                    print('T', end=' ')
                else:
                    print('.', end=' ')
            print(grid.tents_in_row[r])
        for num in grid.tents_in_col:
            print(num, end=' ')
        print()