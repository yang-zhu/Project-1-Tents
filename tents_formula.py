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
        trees = []
        tents_in_row = []
        for lineIndex in range(height):
            (line, tentNum) = f.readline().split()
            tents_in_row.append(int(tentNum))
            for (cellIndex, cell) in enumerate(line):
                if cell == 'T':
                    trees.append((lineIndex, cellIndex))
        tents_in_col = [int(t) for t in f.readline().split()]
        return Grid(height, width, trees, tents_in_row, tents_in_col)

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

grid = gridInput('tent-inputs/tents-8x8-e1.txt')
# No two tents are adjacent in an of the (up to) 8 directions
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

# Every tree matches at most one tent
for (r, c) in grid.trees:
    neighbor_cells = pair_clause_helper(boundFilter([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width))
    for ((r1, c1), (r2, c2)) in neighbor_cells:
        clauses.append((-treeVar(r, c, r1, c1), -treeVar(r, c, r2, c2)))
    
# Every tent matches at least one tree
for r in range(grid.height):
    for c in range(grid.width):
        neighbor_cells = boundFilter([(r-1, c), (r+1, c), (r, c-1), (r, c+1)], grid.height, grid.width)
        clause = [-tentVar(r, c)]
        for (r_n, c_n) in neighbor_cells:
            if (r_n, c_n) in grid.trees:
                clause.append(treeVar(r_n, c_n, r, c))
        clauses.append(tuple(clause))

def countTents(count, row_or_col, dim1, limit):
    '''Every row/column has exactly the required number of tents.'''   
    def dimConv(dim2):
        '''Adapts tentVar to row_or_col.'''
        if row_or_col == 'row':
            return tentVar(dim1, dim2)
        else:
            return tentVar(dim2, dim1)
    
    def countVarConv(count, dim2):
        '''Adapts countVar to row_or_col.'''
        if row_or_col == 'row':
            return countVar(count, dim1, dim2, dim1, limit)
        else:
            return countVar(count, dim2, dim1, limit, dim1)
   
    clauses = []
    if count == 0:
        clauses += [(-dimConv(dim),) for dim in range(limit+1)]
    else:
        clauses.append((-dimConv(0), countVarConv(count-1, 1)))
        clauses.append((dimConv(0), countVarConv(count, 1)))
        for dim2 in range(1, limit+1):
            for num in range(count+1):
                if num < limit + 1 - dim2 and num > 0:
                    clauses.append((-dimConv(dim2), -countVarConv(num, dim2), countVarConv(num-1, dim2+1)))
                    clauses.append((dimConv(dim2), -countVarConv(num, dim2), countVarConv(num, dim2+1)))
                elif num == limit + 1 - dim2:
                    for i in range(dim2, limit+1):
                        clauses.append((-countVarConv(num, dim2), dimConv(i)))
                elif num == 0:
                    for i in range(dim2, limit+1):
                        clauses.append((-countVarConv(num, dim2), -dimConv(i)))
    return clauses


# Every row has exactly the required number of tents
for r in range(grid.height):
    count = grid.tents_in_row[r]
    clauses += countTents(count, 'row', r, grid.width-1)

# Every column has exactly the required number of tents
for c in range(grid.width):
    count = grid.tents_in_col[c]
    clauses += countTents(count, 'column', c, grid.height-1)

# Output the clauses in DIMACS CNF format
print('p', 'cnf', len(varDict), len(clauses))
for clause in clauses:
    print(' '.join(map(str, clause)), '0')

