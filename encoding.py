import subprocess
import argparse
from display_solution import display
import sys
import time
import math

class Grid:  # used for generating CNF formulas
    def __init__(self, height, width, trees, tents_in_row, tents_in_col):
        assert height == len(tents_in_row), width == len(tents_in_col)
        self.height = height
        self.width = width
        self.trees = trees
        # set of unoccupied cells
        self.empty = set((r, c) for r in range(height) for c in range(width) if (r, c) not in trees)
        # set of candidate tent cells (next to trees)
        self.possible_tents = set((r_n, c_n) for (r, c) in self.trees for (r_n, c_n) in self.treeNeighbors(r, c))
        self.tents_in_row = tents_in_row
        self.tents_in_col = tents_in_col
    
    def withinBounds(self, lis):
        '''Filters out out-of-bounds coordinates.'''
        return [(x, y) for (x, y) in lis if x >= 0 and x < self.height if y >= 0 and y < self.width]

    def withinBoundsNoTree(self, lis):
        '''Filters out coordinates that are occupied by trees or out of bounds.'''
        return [(x, y) for (x, y) in self.withinBounds(lis) if (x, y) not in self.trees]
    
    def withinBoundsTrees(self, lis):
        '''Filters out coordinates that are not occupied by trees or out of bounds.'''
        return [(x, y) for (x, y) in self.withinBounds(lis) if (x, y) in self.trees]
    
    def tentNeighbors(self, r, c):
        '''Returns the neighboring cells of a tent that can't have tents.'''
        return self.withinBoundsNoTree([(r_n, c_n) for r_n in [r-1, r, r+1] for c_n in [c-1, c, c+1] if not ((r_n == r) and (c_n == c))])
    
    def treeNeighbors(self, r, c):
        '''Returns the empty neighboring cells of a tree.'''
        return self.withinBoundsNoTree([(r-1, c), (r+1, c), (r, c-1), (r, c+1)])

    @staticmethod
    def fromFile(gridPath):
        '''Reads a puzzle from a file.'''
        with open(gridPath) as f:
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
    
    def printSolution(self, solution):
        '''Prints the solved puzzle.'''
        for r in range(self.height):
            for c in range(self.width):
                if (r, c) in solution:
                    print('Δ', end=' ')
                elif (r, c) in self.trees:
                    print('T', end=' ')
                else:
                    print('.', end=' ')
            print(self.tents_in_row[r])
        for num in self.tents_in_col:
            print(num, end=' ')
        print()

    def printPuzzle(self, f = sys.stdout):
        '''Prints the puzzle (without tents).'''
        print(self.height, self.width, file=f)
        for r in range(self.height):
            for c in range(self.width):
                if (r,c) in self.trees:
                    print('T', end='', file=f)
                else:
                    print('.', end='', file=f)
            print(' ' + str(self.tents_in_row[r]), file=f)
        for c in range(self.width):
            print(self.tents_in_col[c], end=' ', file=f)
        print(file=f)
    

class GridWithTents(Grid):  # used for generating puzzles
    def __init__(self, height, width):
        Grid.__init__(self, height, width, set(), [0 for _ in range(height)], [0 for _ in range(width)])
        self.possible_tents = None
        self.tent_tree_pair = {}  # dictionary that maps every tent to the tree it is bound to
    
    def tents(self):
        return self.tent_tree_pair.keys()  # kept up-to-date

    def addTreeTent(self, tree, tent):
        '''Adds a tree-tent pair to the grid and updates the attributes accordingly.'''
        if tree not in self.empty or tent not in self.empty or any(cell in self.tents() for cell in self.tentNeighbors(*tent)):
            return False
        self.trees.add(tree)
        self.empty.remove(tree)
        self.empty.remove(tent)
        self.tent_tree_pair[tent] = tree
        self.tents_in_row[tent[0]] += 1
        self.tents_in_col[tent[1]] += 1
        return True
    
    def delTreeTent(self, tent):
        '''Removes a tent with its tree from the grid and updates the attributes accordingly.'''
        tree = self.tent_tree_pair[tent]
        self.trees.remove(tree)
        self.empty.add(tree)
        self.empty.add(tent)
        del self.tent_tree_pair[tent]
        self.tents_in_row[tent[0]] -= 1
        self.tents_in_col[tent[1]] -= 1
    
    def withoutTents(self):
        '''Removes tents from a solved puzzle to allow encoding as a formula.'''
        return Grid(self.height, self.width, self.trees, self.tents_in_row, self.tents_in_col)


def solveGrid(cadical_path, grid, excluded_sol=None, tree_without_tent=False, no_binary=False, return_stats=False, timeout=None):
    clauses = [] # Stores all the clauses
    varDict = {}  # Stores all the generated variables

    def generateVar(varDescr):
        '''Generates a variable from the variable description.'''
        if varDescr not in varDict:
            varDict[varDescr] = len(varDict) + 1
        return varDict[varDescr]

    def newVar():
        '''Generates variables without specific descriptions (for binary addtion).'''
        return generateVar(len(varDict))

    def tentVar(r, c):
        '''The generated variable means that the cell at (r, c) contains a tent.'''
        assert r < grid.height and c < grid.width
        assert (r, c) in grid.possible_tents
        return generateVar(('tent', r, c))

    def arrowVar(r, c, r_tent, c_tent):
        '''We use the notion of an arrow pointing from a tree to a tent to model the 1:1 mapping between trees and tents. The generated variable means that there is an arrow pointing from the tree (r, c) to the tent (r_tent, c_tent).'''
        assert r_tent in range(grid.height) and c_tent in range(grid.width)
        assert r in range(grid.height) and c in range(grid.width)
        return generateVar(('arrow', r, c, r_tent, c_tent))

    def countVar(count, start_row, start_col, end_row, end_col):
        '''The generated variable means that the cells from (start_row, start_col) to (end_row, end_col) contain count many tents.'''
        return generateVar(('count', count, start_row, start_col, end_row, end_col))

    # Generates impossible clauses for future use, namely when the number of expected tents in a row/column is larger than the number of empty cells. See countTents.
    dummyVar = newVar()
    impossible_clauses = [(dummyVar,), (-dummyVar,)]


    # Rules out the given solution (for generating puzzles with unique solutions).
    if excluded_sol != None:
        clauses.append(tuple(-tentVar(*cell) for cell in excluded_sol))


    # Aborts the encoding immediately after detecting the mismatch between the number of trees and tents globally.
    if tree_without_tent and not len(grid.trees) == sum(grid.tents_in_row) == sum(grid.tents_in_col):
        return None


    # No two tents are adjacent in any of the (up to) 8 directions.
    for (r1, c1) in grid.possible_tents:
        for (r2, c2) in grid.tentNeighbors(r1, c1):
            if (r2, c2) in grid.possible_tents:
                clauses.append((-tentVar(r1, c1), -tentVar(r2, c2)))


    def pair_clause_helper(lis):
        '''Chooses 2 variables out of a list to build clauses.'''
        return [(ele1, ele2) for ele1 in lis for ele2 in lis if ele2 != ele1]

    for (r, c) in grid.trees:
        neighbor_cells = grid.treeNeighbors(r,c)

        if not tree_without_tent:  # for the version of encoding that forces a 1:1 mapping between trees and tents
            # Every arrow points to a tent.
            clauses += [(-arrowVar(r, c, r1, c1), tentVar(r1, c1)) for (r1, c1) in neighbor_cells]
            
            # Every tree has at least one arrow.
            clause = tuple(arrowVar(r, c, r1, c1) for (r1, c1) in neighbor_cells)   
            clauses.append(clause)    
        
        # Every tree has at most one arrow.
        for ((r1, c1), (r2, c2)) in pair_clause_helper(neighbor_cells):
            clauses.append((-arrowVar(r, c, r1, c1), -arrowVar(r, c, r2, c2)))
        
    # For every tent there is exactly one arrow pointing to it.
    for (r, c) in grid.possible_tents:
        tree_cells = grid.withinBoundsTrees([(r-1, c), (r+1, c), (r, c-1), (r, c+1)])
        
        # For every tent there is at least one arrow pointing to it.
        clause = [-tentVar(r, c)]
        clause += [arrowVar(r1, c1, r, c) for (r1, c1) in tree_cells]
        clauses.append(tuple(clause))
        
        if not tree_without_tent:
            # There is at most one arrow pointing to a tent.
            clauses += [(-arrowVar(r1, c1, r, c), -arrowVar(r2, c2, r, c)) for ((r1, c1), (r2, c2)) in pair_clause_helper(tree_cells)]


    def countTents(count, empty_cells):
        '''Ensures that the number of tents in empty_cells matches count.'''
        if count > len(empty_cells):
            return impossible_clauses
        
        if not no_binary:  # for the version of encoding that uses binary addition
            return bitCountTents(count, empty_cells)
        
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
    
    def halfAdder(b1, b2):
        '''Computes the sum of two bits.'''
        bit_sum = newVar()
        carry = newVar()
        clauses.append((b1, b2, -bit_sum))
        clauses.append((b1, -b2, bit_sum))
        clauses.append((-b1, b2, bit_sum))
        clauses.append((-b1, -b2, -bit_sum))
        clauses.append((-b1, -b2, carry))
        clauses.append((b1, -carry))
        clauses.append((b2, -carry))
        return (bit_sum, carry)

    def fullAdder(b1, b2, b3):
        '''Computes the sum of three bits.'''
        bit_sum = newVar()
        carry = newVar()
        clauses.append((b1, b2, b3, -bit_sum))
        clauses.append((b1, b2, -b3, bit_sum))
        clauses.append((b1, -b2, b3, bit_sum))
        clauses.append((b1, -b2, -b3, -bit_sum))
        clauses.append((-b1, b2, b3, bit_sum))
        clauses.append((-b1, b2, -b3, -bit_sum))
        clauses.append((-b1, -b2, b3, -bit_sum))
        clauses.append((-b1, -b2, -b3, bit_sum))
        clauses.append((-b1, -b2, carry))
        clauses.append((-b1, -b3, carry))
        clauses.append((-b2, -b3, carry))
        clauses.append((b1, b2, -carry))
        clauses.append((b1, b3, -carry))
        clauses.append((b2, b3, -carry))
        return (bit_sum, carry) 

    def binaryAddition(l1, l2):
        '''Computes the sum of two binary numbers.'''
        result = []
        carry = None
        for (i, pair) in enumerate(zip(l1, l2)):
            if i == 0:
                (bit_sum, carry) = halfAdder(*pair)
                result.append(bit_sum)
            else:
                (bit_sum, carry) = fullAdder(*pair, carry)
                result.append(bit_sum)
        if len(l1) < len(l2):
            result.extend(halfAdder(l2[-1], carry))
        elif len(l1) > len(l2):
            result.extend(halfAdder(l1[-1], carry))
        else:
            result.append(carry)
        return result

    def bitCount(l):
        '''Computes the number of tents in a row or column as a binary number.'''
        if len(l) == 1:
            return [tentVar(*l[0])] 
        else:
            middle = len(l) // 2
            return binaryAddition(bitCount(l[:middle]), bitCount(l[middle:]))
    
    def bitCountTents(count, empty_cells):
        '''Computes the number of tents in empty_cells as a binary number and makes sure that this matches the binary representation of count.'''
        if empty_cells == [] and count == 0:
            return []
        res = bitCount(empty_cells)
        for i in range(len(res)):
            bit = count % 2
            if bit == 0:
                res[i] = -res[i]
            count = count // 2
        return [(lit,) for lit in res]   

    # Every row has exactly the required number of tents.
    for r in range(grid.height):
        count = grid.tents_in_row[r]
        clauses += countTents(count, [(r, c) for c in range(grid.width) if (r, c) in grid.possible_tents])

    # Every column has exactly the required number of tents.
    for c in range(grid.width):
        count = grid.tents_in_col[c]
        clauses += countTents(count, [(r, c) for r in range(grid.height) if (r, c) in grid.possible_tents])

    # Remove duplicate clauses.
    clauses = set(tuple(sorted(clause)) for clause in clauses)

    # Output the clauses in DIMACS CNF format as a string.
    res = 'p cnf ' + str(len(varDict)) + ' ' + str(len(clauses)) + '\n'
    res += '\n'.join([' '.join(map(str, clause)) + ' 0' for clause in clauses]) + '\n'
    
    # Record the statistics: number of variables, number of clauses, running time of CaDiCaL.
    stats = {}  
    stats['Variables'] = len(varDict)
    stats['Clauses'] = len(clauses)

    start = time.time()

    # Feed the CNF formula into CaDiCaL.
    solver_process = subprocess.Popen([cadical_path, '-q'], stdin = subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
    try:
        (solution, _) = solver_process.communicate(input = res, timeout = timeout)
    except subprocess.TimeoutExpired:
        # Abort the solver when timeout is reached and return infinity as solving time.
        solver_process.kill()
        if return_stats:
            stats['Solving time'] = math.inf
            return stats
        else:
            raise

    end = time.time()
        
    if return_stats:
        stats['Solving time'] = end - start
        return stats

    positive = set()  # stores all the positiv assignments, including the locations of tents
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
    
    tents = set((r, c) for (r, c) in grid.possible_tents if tentVar(r, c) in positive)  # stores all the cells with tents
    
    return tents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve 'Tents' puzzles.")
    parser.add_argument('cadical', help='path to CaDiCaL')
    parser.add_argument('input_file', help='height of the grid')
    parser.add_argument('-i', '--image', action='store_true', help='display the solution graphically')
    parser.add_argument('-t','--tree_without_tent', action='store_true', help='allow trees without tents')
    parser.add_argument('-n', '--no_binary', action='store_true', help='disable binary addition to count tents')
    args = parser.parse_args()

    grid = Grid.fromFile(args.input_file)
    solution = solveGrid(args.cadical, grid, tree_without_tent=args.tree_without_tent, no_binary=args.no_binary)

    # Print the solution on the terminal and displays the solution graphically when the flag -i is enabled.
    if solution == None:
        print('UNSATISFIABLE')
    else:
        grid.printSolution(solution)
        if args.image:
            display(grid, solution)
        
    
    
