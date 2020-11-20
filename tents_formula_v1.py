import subprocess
import sys

if len(sys.argv) != 3:
    print('Please input two arguments: <path of the CaDiCal prorgam> <path of the grid file>')
    exit(1)

class Grid:
    def __init__(self, height, width, trees, tents_in_row, tents_in_col):
        assert height == len(tents_in_row), width == len(tents_in_col)
        self.height = height
        self.width = width
        self.trees = trees
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
        return Grid(height, width, trees, tents_in_row, tents_in_col)

grid = gridInput(sys.argv[2])
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
    return generateVar(('tent', r, c))

def treeVar(r, c, r_tent, c_tent):
    '''The tree in cell (r, c) matches the tent in cell (r_tent, c_tent).'''
    assert r_tent in range(grid.height) and c_tent in range(grid.width)
    assert r in range(grid.height) and c in range(grid.width)
    return generateVar(('tree', r, c, r_tent, c_tent))

def countVar(count, start_row, start_col, end_row, end_col):
    '''The cells from (start_row, start_col) to (end_row, end_col) contain count many tents.'''
    return generateVar(('count', count, start_row, start_col, end_row, end_col))

def boundFilter(lis, height, width):
    '''Filters out coordinates that are out of bounds of a grid.'''
    return [(x,y) for (x,y) in lis if x >=0 and x < height if y >= 0 and y < width]

def noTentIndex(r, c):
    '''Neighboring cells of a cell with tent can't have tents.'''
    return boundFilter([(r_n, c_n) for r_n in [r-1, r, r+1] for c_n in [c-1, c, c+1] if not ((r_n == r) and (c_n == c))], grid.height, grid.width)


# No two tents are adjacent in any of the (up to) 8 directions
for r1 in range(grid.height):
    for c1 in range(grid.width):
        for (r2, c2) in noTentIndex(r1, c1):
            clauses.append((-tentVar(r1, c1), -tentVar(r2, c2)))

# Cells with trees can't contain tents
for (r, c) in grid.trees:
    clauses.append((-tentVar(r,c),))


def pair_clause_helper(lis):
    '''Chooses 2 variables out of a list to build clauses.'''
    return [(ele1, ele2) for ele1 in lis for ele2 in lis if ele2 != ele1]

# Every tree has exactly one arrow
for (r, c) in grid.trees:
    neighbor_cells = boundFilter([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width)

    # Every arrow points to a tent
    clauses += [(-treeVar(r, c, r1, c1), tentVar(r1, c1)) for (r1, c1) in neighbor_cells]
    
    # Every tree has at least one arrow
    clause = tuple(treeVar(r, c, r1, c1) for (r1, c1) in neighbor_cells)   
    clauses.append(clause)    
    
    # Every tree has at most one arrow
    for ((r1, c1), (r2, c2)) in pair_clause_helper(neighbor_cells):
        clauses.append((-treeVar(r, c, r1, c1), -treeVar(r, c, r2, c2)))
    
# There is exactly one arrow pointing to every tent
for r in range(grid.height):
    for c in range(grid.width):
        neighbor_cells = boundFilter([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width)
        tree_cells = [cell for cell in neighbor_cells if cell in grid.trees]
        
        # There is at least one arrow pointing to every tent
        clause = [-tentVar(r, c)]
        clause += [treeVar(r1, c1, r, c) for (r1, c1) in tree_cells]
        clauses.append(tuple(clause))
        
        # There is at most one arrow pointing to every tent
        clauses += [(-treeVar(r1, c1, r, c), -treeVar(r2, c2, r, c)) for ((r1, c1), (r2, c2)) in pair_clause_helper(tree_cells)]


def countTents(count, row_or_col, dim1, limit):
    '''Every row/column has exactly the required number of tents.'''   
    def tentVarSwap(dim2):
        '''Adapts tentVar to row_or_col.'''
        if row_or_col == 'row':
            return tentVar(dim1, dim2)
        else:
            return tentVar(dim2, dim1)
    
    def countVarSwap(count, dim2):
        '''Adapts countVar to row_or_col.'''
        if row_or_col == 'row':
            return countVar(count, dim1, dim2, dim1, limit)
        else:
            return countVar(count, dim2, dim1, limit, dim1)
   
    clauses = []
    if count == 0:
        clauses += [(-tentVarSwap(dim),) for dim in range(limit+1)]
    else:
        clauses.append((-tentVarSwap(0), countVarSwap(count-1, 1)))
        clauses.append((tentVarSwap(0), countVarSwap(count, 1)))
        for dim2 in range(1, limit+1):
            for num in range(count+1):
                if num < limit + 1 - dim2 and num > 0:
                    clauses.append((-tentVarSwap(dim2), -countVarSwap(num, dim2), countVarSwap(num-1, dim2+1)))
                    clauses.append((tentVarSwap(dim2), -countVarSwap(num, dim2), countVarSwap(num, dim2+1)))
                elif num == limit + 1 - dim2:
                    for i in range(dim2, limit+1):
                        clauses.append((-countVarSwap(num, dim2), tentVarSwap(i)))
                elif num == 0:
                    for i in range(dim2, limit+1):
                        clauses.append((-countVarSwap(num, dim2), -tentVarSwap(i)))
    return clauses

# Every row has exactly the required number of tents
for r in range(grid.height):
    count = grid.tents_in_row[r]
    clauses += countTents(count, 'row', r, grid.width-1)

# Every column has exactly the required number of tents
for c in range(grid.width):
    count = grid.tents_in_col[c]
    clauses += countTents(count, 'column', c, grid.height-1)


# Output the clauses in DIMACS CNF format as a string
res = 'p cnf ' + str(len(varDict)) + ' ' + str(len(clauses)) + '\n'
res += '\n'.join([' '.join(map(str, clause)) + ' 0' for clause in clauses]) + '\n'

print("running solver with", len(varDict), "variables and", len(clauses), "clauses...")

# Feeds the cnf formula into CaDiCal
solver_process = subprocess.Popen([sys.argv[1], '-q'], stdin = subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')

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
        print('UNSATISFIABLE')
        exit()
         

# Generates the solution grid
for r in range(grid.height):
    for c in range(grid.width):
        if tentVar(r, c) in positive:
            print('Δ', end=' ')
        elif (r, c) in grid.trees:
            print('T', end=' ')
        else:
            print('.', end=' ')
    print(grid.tents_in_row[r])
for num in grid.tents_in_col:
    print(num, end=' ')
print()
