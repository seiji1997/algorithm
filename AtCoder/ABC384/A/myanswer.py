# This is the myanswer.py for problem A in ABC384
N, c1, c2 = input().split()
N = int(N)
S = input().strip()

result = []
for ch in S:
    if ch == c1:
        result.append(ch)
    else:
        result.append(c2)

print("".join(result))
