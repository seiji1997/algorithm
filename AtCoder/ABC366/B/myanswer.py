N = int(input())
S = [input().strip() for _ in range(N)]
M = max(len(s) for s in S)
T = []

for j in range(M):
    new_row = []
    for i in range(N):
        if j < len(S[N - i - 1]):
            new_row.append(S[N - i - 1][j])
        else:
            new_row.append('*')
    T.append(''.join(new_row))

for t in T:
    print(t.rstrip('*'))
