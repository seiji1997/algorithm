# A - Sort Left and Right
# https://atcoder.jp/contests/arc181/tasks/arc181_a
# 指定された操作を繰り返し行うことで、与えられた順列を昇順にソートするための最小の操作回数を求める問題

"""
操作回数の計算方針: 
- 各順列がすでにソートされているかをチェック(順列を順番に見ていき、連続する部分が順序通りかどうかを確認)
  - ソートされている場合: 操作不要のため0を記録
  - ソートされていない場合: 順序が乱れている最初と最後のインデックスを特定し、その範囲がソートされているかを確認
    - 乱れた部分が一つのブロックであれば、1回の操作でソート可能
    - それ以外の場合は、2回の操作でソート可能
"""

# AC 69ms, 30956KB

import sys

def input():
    return sys.stdin.readline().strip()

def is_already_sorted(P, N):
    """Check if the permutation is already sorted."""
    return P == list(range(1, N + 1))

def is_special_case(P, N):
    """Check if the permutation is the special case where P[0] is N and P[-1] is 1."""
    return P[0] == N and P[-1] == 1

def can_sort_in_one_operation(P, N):
    """Determine if the permutation can be sorted with a single operation."""
    max_value_seen = 0
    for i in range(N):
        if P[i] == i + 1 and max_value_seen < i + 1:
            return True
        if P[i] > max_value_seen:
            max_value_seen = P[i]
    return False

def calculate_min_operations(N, P):
    if is_special_case(P, N):
        return 3
    if is_already_sorted(P, N):
        return 0
    if can_sort_in_one_operation(P, N):
        return 1
    return 2

def main():
    T = int(input())
    for _ in range(T):
        N = int(input())
        P = list(map(int, input().split()))
        print(calculate_min_operations(N, P))

if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------------
# AC 173ms, 32296KB
def calculate_min_operations(N, A):
    # Create a list to mark misplacements
    misplacements = [1 if A[i] != i + 1 else 0 for i in range(N)]
    
    if sum(misplacements) == 0:
        # The array is already sorted
        return 0
    elif A[0] == N and A[-1] == 1:
        # Edge case where first element is N and last element is 1
        return 3
    elif misplacements[0] == 0 or misplacements[-1] == 0:
        # At least one end is already sorted
        return 1
    else:
        # Check if there is a continuous sorted segment
        for i in range(1, N):
            if misplacements[i] == 0:
                if all(A[j] <= i + 1 for j in range(i)):
                    return 1
        return 2

def main():
    import sys
    input = sys.stdin.read
    data = input().split()

    index = 0
    T = int(data[index])
    index += 1

    results = []
    for _ in range(T):
        N = int(data[index])
        index += 1
        A = list(map(int, data[index:index + N]))
        index += N

        results.append(calculate_min_operations(N, A))

    for result in results:
        print(result)

if __name__ == "__main__":
    main()
