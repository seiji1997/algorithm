# This is the myanswer.py for problem B in ABC377
def count_available_cells(grid):
    rows_with_hash = set()
    cols_with_hash = set()

    for i in range(8):
        for j in range(8):
            if grid[i][j] == "#":
                rows_with_hash.add(i)
                cols_with_hash.add(j)

    row_blocked = len(rows_with_hash) * 8
    col_blocked = len(cols_with_hash) * (8 - len(rows_with_hash))
    total_blocked = row_blocked + col_blocked
    available_cells = 64 - total_blocked

    return available_cells


grid = list(map(str.strip, [input() for _ in range(8)]))
print(count_available_cells(grid))
