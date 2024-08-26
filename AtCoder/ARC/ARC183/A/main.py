# 辞書順で floor((S+1)/2) 番目の整数列を計算
"""
N: 異なる整数の種類数 (1からNまで)
K: 各整数が登場する回数
"""
# import math
# import itertools

# def find_sequence(N, K):
#     fact = math.factorial    
#     S = fact(N * K) // (fact(K) ** N)
#     target = (S + 1) // 2 
    
#     sequence = []
#     remaining_counts = [K] * N
#     remaining_target = target
    
#     for _ in range(N * K):
#         for i in range(1, N + 1):
#             if remaining_counts[i - 1] == 0:
#                 continue
            
#             remaining_counts[i - 1] -= 1
#             current_pattern_count = fact(sum(remaining_counts)) // \
#                                     math.prod([fact(x) for x in remaining_counts])
            
#             if remaining_target <= current_pattern_count:
#                 sequence.append(i)
#                 break
#             else:
#                 remaining_target -= current_pattern_count
#                 remaining_counts[i - 1] += 1
    
#     return sequence

# N, K = map(int, input().split())
# result = find_sequence(N, K)
# print(" ".join(map(str, result)))


# -------------------------------------------------------

import math
from functools import lru_cache

@lru_cache(None)
def factorial(x):
    return math.factorial(x)

def find_nice_sequence(N, K):
    S = factorial(N * K) // (factorial(K) ** N)
    
    target = (S + 1) // 2
    
    sequence = []
    remaining_counts = [K] * N
    remaining_target = target
    
    for _ in range(N * K):
        current_sum = sum(remaining_counts)
        for i in range(1, N + 1):
            if remaining_counts[i - 1] == 0:
                continue
            
            remaining_counts[i - 1] -= 1
            
            current_pattern_count = factorial(current_sum - 1) // \
                                    math.prod([factorial(x) for x in remaining_counts])
            
            if remaining_target <= current_pattern_count:
                sequence.append(i)
                break
            else:
                remaining_target -= current_pattern_count
                remaining_counts[i - 1] += 1
    
    return sequence

N, K = map(int, input().split())
result = find_nice_sequence(N, K)
print(" ".join(map(str, result)))
