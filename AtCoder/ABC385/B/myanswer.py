# This is the myanswer.py for problem B in ABC385
import sys


def solve():

    input = sys.stdin.readline
    H, W, sr, sc = map(int, input().split())
    board = [list(input().rstrip("\n")) for _ in range(H)]
    commands = input().rstrip("\n")

    r = sr - 1
    c = sc - 1

    collected = 0

    for cmd in commands:
        nr, nc = r, c

        if cmd == "L":
            nc -= 1
        elif cmd == "R":
            nc += 1
        elif cmd == "U":
            nr -= 1
        elif cmd == "D":
            nr += 1

        if board[nr][nc] != "#":
            r, c = nr, nc
            if board[r][c] == "@":
                collected += 1
                board[r][c] = "."

    print(r + 1, c + 1, collected)


solve()
