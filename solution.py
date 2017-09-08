ROW = "ABCDEFGHI"
COL = "abcdefghi"

product = lambda row,col:[r+c for r in row for c in col]
REGION = {
    'topLeft':product('ABC','abc'),    'top':product('ABC','def'),    'topRight':product('ABC','ghi'),
    'left':product('DEF','abc'),       'center':product('DEF','def'), 'right':product('DEF','ghi'),
    'bottomLeft':product('GHI','abc'), 'bottom':product('GHI','def'), 'bottomRight':product('GHI','ghi')
}


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    gi = iter(grid)
    values = {}

    for r in ROW:
        for c in COL:
            g = next(gi)
            values[r+c] = g if g != '.' else '123456789'

    return values

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def eliminate(values):
    for r in ROW:
        for c in COL:
            if len(values[r+c]) > 1:
                continue

            val = values[r+c]
            
            # Eliminate over row
            for cc in COL:
                if val in values[r+cc] and c != cc:
                    e = values[r+cc].replace(val,'')
                    assign_value(values,r+cc,e)
            # Eliminate over col
            for rr in ROW:
                if val in values[rr+c] and r != rr:
                    e = values[rr+c].replace(val,'')
                    assign_value(values,rr+c,e)
            # Eliminate over region
            for regKey,regVal in REGION.items():
                if r+c in regVal:
                    for rv in regVal:
                        if val in values[rv] and r+c != rv:
                            e = values[rv].replace(val,'')
                            assign_value(values,rv,e)
                    break

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """

    def find_naked(pairs):
        single = set()
        for p in pairs:
            if p not in single:
                single.add(p)
            else:
                yield p
                
    def eliminate_naked(naked,group,values):
        """Eliminate naked values
        Args:
            naked: length 2 string
            group: sub dict of values, a dictionary of the form {'box_name': '123456789', ...}
            values(dict): a dictionary of the form {'box_name': '123456789', ...}
        """
        for box,value in group.items():
            if value != naked:
                e = value.replace(naked[0],"")
                e =     e.replace(naked[1],"")
                assign_value(values,box,e)
    
    # Find and eliminate naked pairs over row
    for r in ROW:
        pairs = [values[r+c] for c in COL if len(values[r+c])==2]
        naked = list(find_naked(pairs))
        if naked:
            # group should not put out of loop
            # otherwise eliminate naked pairs may fail
            for nake in naked:
                group = {box:value for box,value in values.items() if r in box}
                eliminate_naked(nake,group,values)
                
    # Find and eliminate naked pairs over col
    for c in COL:
        pairs = [values[r+c] for r in ROW if len(values[r+c])==2]
        naked = list(find_naked(pairs))
        if naked:
            for nake in naked:
                group = {box:value for box,value in values.items() if c in box}
                eliminate_naked(nake,group,values)
    
    # Find and eliminate naked pairs over region
    for region,boxes in REGION.items():
        pairs = [values[box] for box in boxes if len(values[box])==2]
        naked = list(find_naked(pairs))
        if naked:
            for nake in naked:
                group = {box:values[box] for box in boxes}
                eliminate_naked(nake,group,values)

from collections import Counter
def only_square(values):
    """Assign values using the only square strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """
    
    def find_only_square(possibilities):
        """Find only squares.
        Args:
            possibilities: sub dict of values, a dictionary of the form {'box_name': '123456789', ...}
            
        Yields:
            a tuple form (box, only value)
        """
        counter = Counter("".join(possibilities.values()))
        only = [p for p,c in counter.items() if c == 1]
        if only:
            for p in only:
                for box,value in possibilities:
                    if p in value:
                        yield box,p
                        break
        
    
    # Check only square over row group
    for r in ROW:
        possibilities = {box:value for box,value in values.items() if r in box and len(value)>1 } 
        onlySquare = list(find_only_square(possibilities))
        if onlySquare:
            for box,val in onlySquare:
                assign_value(values,box,val)
    
    # Check only square over col group
    for c in COL:
        possibilities = {box:value for box,value in values.items() if c in box and len(value)>1 } 
        onlySquare = list(find_only_square(possibilities))
        if onlySquare:
            for box,val in onlySquare:
                assign_value(values,box,val)
    
    # Check only square over region group
    for region,boxes in REGION.items():
        possibilities = {box:values[box] for box in boxes if len(values[box])>1 }
        onlySquare = list(find_only_square(possibilities))
        if onlySquare:
            for box,val in onlySquare:
                assign_value(values,box,val)

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    s = "{:^9s}|{:^9s}|{:^9s}|{:^9s}|{:^9s}|{:^9s}|{:^9s}|{:^9s}|{:^9s}"
    for i,r in enumerate(ROW):
        if i%3 == 0:
            print(s.format(*['-'*9]*9))
        print(s.format(*[values[r+c] for c in COL]))
    print(s.format(*['-'*9]*9))

from copy import deepcopy

isValid = lambda values: "" not in values.values()

def isValidSolution(values):
    return all([len(val)==1 for val in values.values()])

def dfs(values,assignments):
    # backup
    values_copy = deepcopy(values)
    assignments_copy = deepcopy(assignments)
    
#     display(values)
    candidates = [box for box in product(ROW,COL) if len(values[box])>1]
    box = candidates[0]
    
    for val in values[box]:
        print("Try: assign {} to {}".format(val,box))
        assign_value(values,box,val)

        while not isValidSolution(values):
            N = len(assignments)
            eliminate(values)
            only_square(values)
            naked_twins(values)
            if len(assignments) == N:
                break
        
        print('eliminate...........')
        display(values)
        if isValid(values):
            if isValidSolution(values):
                return True,values
            else:
                print("Go deeper.")
                flag,values = dfs(values,assignments)
                if flag:
                    return True,values
                else:
                    print("Fail in deeper level.")
        
        print("Attempt fail.")
        values = deepcopy(values_copy)
        assignments = deepcopy(assignments_copy)
    
    return False,None




def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    global assignments
    assignments = []
    values = grid_values(grid)
    
    while not isValidSolution(values):
        N = len(assignments)
    #     display(values)
        eliminate(values)
        only_square(values)
        naked_twins(values)
        if len(assignments) == N:
            break

    print("After eliminate possibilities.")
    display(values)
    
    if not isValidSolution(values):
        print('Searching...')
        flag,values = dfs(values,assignments)
    
    print("Succeed!")
    return values

if __name__ == '__main__':
    sudoku_grid_1 = '3.7.2..94....49371.4937....874.93...9..8174.3..345.789.....584.2..7......3..8...7'
    sudoku_grid_2 = '7.....2181........9.62.87....34276.....9.6.....75813....93.58.4........9874.....3'
    sudoku_grid_3 = '..6.4.52.2....6..41....96...2.6...8......8....1.5...4.3....71..9....2..8..7.9.43.'
    sudoku_grid_4 = '39....1...482........4.7...5..72....9..1.6..7....39..8...9.5........127...1....63'
    sudoku_grid_5 = '.1..398.......7..4273.........75..8.8....3......21..6.951...........4..1.6..957..'
    sudoku_grid_6 = '.7.6..49....7.91..3..15.....62....7.......2.8.41....5.6..57.......9.65...1.8..72.'
    display(solve(sudoku_grid_1))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
