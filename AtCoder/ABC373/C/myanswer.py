# This is the myanswer.py for problem C in ABC373
N = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

max_A = max(A)
max_B = max(B)

print(max_A + max_B)
