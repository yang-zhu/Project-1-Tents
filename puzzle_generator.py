import sys
from random import randrange

if len(sys.argv) != 4:
    print('Please input three arguments: <number of rows> <number of columns> <fill rate>')
    exit(1)

def boundFilter(lis, b1, b2):
    '''Filters out coordinates that are out of bounds of a grid.'''
    return [(x,y) for (x,y) in lis if x >=0 and x < b1 if y >= 0 and y < b2]

def tentCells(r, c, h, w):
    return boundFilter([(x, y) for (x, y) in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]], h, w)

def noTentCells(r, c, h, w):
    return boundFilter([(x, y) for x in [r-1, r, r+1] for y in [c-1, c, c+1] if not ((x == r) and (y == c))], h, w)


def generateGrid(height, width, percent):
    puzzle = {(r,c): '.' for r in range(height) for c in range(width)}
    p = 0
    loop_count = 0 
    while p <= percent:
        # count how many times the while-loop is executed without adding new trees
        loop_count += 1
        if loop_count > 50000:
            break
        
        (rowInd, colInd) = (randrange(height), randrange(width))
        tents = tentCells(rowInd, colInd, height, width)
        dir = randrange(len(tents))
        no_tents = noTentCells(*tents[dir], height, width)

        if puzzle[(rowInd, colInd)] == '.':
            if puzzle[tents[dir]] == '.':
                if all(puzzle[cell] != 'Δ' for cell in no_tents):
                    puzzle[(rowInd, colInd)] = 'T'
                    puzzle[tents[dir]] = 'Δ'
                    p += 2 / (height * width)
                    loop_count = 0
    return puzzle

height = int(sys.argv[1])
width = int(sys.argv[2])
grid = generateGrid(height, width, float(sys.argv[3]))

print(height, width)
for r in range(height):
    row_count = 0
    for c in range(width):
        if grid[(r,c)] == 'Δ':
            row_count += 1
            print('.', end='')
        else:
            print(grid[(r,c)], end='')
    print(' ' + str(row_count))

for c in range(width):
    col_count = 0
    for r in range(height):
        if grid[(r,c)] == 'Δ':
            col_count += 1
    print(col_count, end=' ') 
