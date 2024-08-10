# This is the myanswer.py for problem A in ABC366 
N, T, A = map(int, input().split())
vote_count = (N // 2) + 1
print("Yes" if T >= vote_count or A >= vote_count else "No")
