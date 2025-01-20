# This is the myanswer.py for problem B in ABC389
import sys


def find_n_factorial(x):
    factorial = 1
    n = 1
    while factorial < x:
        n += 1
        factorial *= n
    if factorial == x:
        return n
    else:
        return -1


input_line = sys.stdin.read().strip()
X = int(input_line)

result = find_n_factorial(X)
print(result)
