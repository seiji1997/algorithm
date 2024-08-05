# A - Sort Left and Right
# https://atcoder.jp/contests/arc181/tasks/arc181_a
# 指定された操作を繰り返し行うことで、与えられた順列を昇順にソートするための最小の操作回数を求める問題

"""
操作回数の計算方針: 
- 各順列がすでにソートされているかをチェック(順列を順番に見ていき、連続する部分が順序通りかどうかを確認)
  - ソートされている場合: 操作不要のため0を記録
  - P[0] is N and P[-1] is 1は3回のsortが必要
  - ソートされていない場合: 順序が乱れている最初と最後のインデックスを特定し、その範囲がソートされているかを確認
    - 乱れた部分が一つのブロックであれば、1回の操作でソート可能
    - それ以外の場合は、2回の操作でソート可能
"""

# AC 69ms, 30956KB

import sys

def input():
    return sys.stdin.readline().strip()

def is_sorted(P, N):
    """Check if the permutation is already sorted."""
    return P == list(range(1, N + 1))

def three_sort(P, N):
    """Check if the permutation is the special case where P[0] is N and P[-1] is 1."""
    return P[0] == N and P[-1] == 1

def one_sort(P, N):
    """Determine if the permutation can be sorted with a single operation."""
    max_value_seen = 0
    for i in range(N):
        if P[i] == i + 1 and max_value_seen < i + 1:
            return True
        if P[i] > max_value_seen:
            max_value_seen = P[i]
    return False

def calculate_sort(N, P):
    if three_sort(P, N):
        return 3
    if is_sorted(P, N):
        return 0
    if one_sort(P, N):
        return 1
    return 2

def main():
    T = int(input())
    for _ in range(T):
        N = int(input())
        P = list(map(int, input().split()))
        print(calculate_sort(N, P))

if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------------
# 提出用
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    P = list(map(int, input().split()))
    if P[0] == N and P[-1] == 1:
        print(3)
    elif P == list(range(1, N + 1)):
        print(0)
    else:
        m = 0
        for i in range(N):
            if P[i] == i + 1 and m < i + 1:
                print(1)
                break
            if P[i] > m:
                m = P[i]
        else:
            print(2)
