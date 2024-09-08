def solve(S, T):
    n = len(S)
    X = []
    S = list(S)

    for i in range(n):
        if S[i] != T[i]:
            S[i] = T[i]
            X.append("".join(S))

    print(len(X))
    for x in X:
        print(x)


S = input().strip()
T = input().strip()

solve(S, T)
