#!/usr/bin/env python3
# This is the main.py for problem B in ABC366

def process(N, S, M):
    T = []
    for j in range(M):
        new_row = []
        for i in range(N):
            if j < len(S[N - i - 1]):
                new_row.append(S[N - i - 1][j])
            else:
                new_row.append("*")
        T.append("".join(new_row))
    return T

def output(T):
    for t in T:
        print(t.rstrip("*"))

def main():
    N = int(input())
    S = [input().strip() for _ in range(N)]
    M = max(len(s) for s in S)
    
    T = process(N, S, M)
    output(T)

if __name__ == '__main__':
    main()
