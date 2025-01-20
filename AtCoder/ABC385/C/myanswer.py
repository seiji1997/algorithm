# This is the myanswer.py for problem C in ABC385
import sys


def solve():
    input = sys.stdin.readline

    N = int(input())
    H = list(map(int, input().split()))

    positions_map = {}
    for i, h in enumerate(H, start=1):
        if h not in positions_map:
            positions_map[h] = []
        positions_map[h].append(i)

    answer = 1

    for h, P in positions_map.items():
        P.sort()
        M = len(P)

        if M == 1:
            answer = max(answer, 1)
            continue

        dp = [dict() for _ in range(M)]
        local_max = 1

        for j in range(M):
            for i in range(j):
                d = P[j] - P[i]  # 公差
                if d in dp[i]:
                    dp[j][d] = dp[i][d] + 1
                else:
                    dp[j][d] = 2
                local_max = max(local_max, dp[j][d])

        answer = max(answer, local_max)

    print(answer)


solve()
