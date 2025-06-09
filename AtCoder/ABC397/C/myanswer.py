import sys


def left_distinct_counts(N, A):
    left = [0] * (N + 1)
    seen = set()
    for i in range(N):
        seen.add(A[i])
        left[i + 1] = len(seen)
    return left


def right_distinct_counts(N, A):
    right = [0] * (N + 1)
    seen = set()
    for i in range(N - 1, -1, -1):
        seen.add(A[i])
        right[i] = len(seen)
    return right


def max_distinct_sum(N, A):
    left = left_distinct_counts(N, A)
    right = right_distinct_counts(N, A)
    max_value = 0
    for i in range(1, len(A)):
        max_value = max(max_value, left[i] + right[i])
    return max_value


input = sys.stdin.readline
N = int(input().strip())
A = list(map(int, input().split()))
result = max_distinct_sum(N, A)
print(result)
