# This is the myanswer.py for problem B in ABC361

def min_max_difference(N, K, A):
    A.sort()
    min_diff = float('inf')
    
    for i in range(N - K + 1):
        current_diff = A[i + (N - K - 1)] - A[i]
        if current_diff < min_diff:
            min_diff = current_diff
    
    return min_diff

N, K = map(int, input().split())
A = list(map(int, input().split()))

print(min_max_difference(N, K, A))

# -----------------------------------

import sys
input = sys.stdin.read
data = input().split()

N = int(data[0])
K = int(data[1])
A = list(map(int, data[2:]))

def find_min_diff(N, K, A):
    A.sort()
    min_diff = float('inf')
    
    for i in range(K + 1):
        diff = A[i + (N - K) - 1] - A[i]
        if diff < min_diff:
            min_diff = diff
    
    return min_diff

result = find_min_diff(N, K, A)
print(result)%                      



