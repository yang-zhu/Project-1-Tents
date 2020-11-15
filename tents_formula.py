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
    return generateVar(('tent', r, c))

def noTentIndex(r, c):
    '''Neighboring cells of a cell with tent can't have tents.'''
    return [(r_n, c_n) for r_n in [r-1, r, r+1] if r_n >= 0 for c_n in [c-1, c, c+1] if c_n >= 0 if not ((r_n == r) and (c_n == c))]

grid = gridInput('tent-inputs/tents-8x8-e1.txt')
for r1 in range(grid.height):
    for c1 in range(grid.width):
        for (r2, c2) in noTentIndex(r1, c1):
            clauses.append((-tentVar(r1, c1), -tentVar(r2, c2)))

# Cells with trees can't contain tents
for (r, c) in grid.trees:
    clauses.append((-tentVar(r,c),))
