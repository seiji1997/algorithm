# This is the myanswer.py for problem A in ABC373

S = [input().strip() for _ in range(12)]

count = 0
for i in range(12):
    if len(S[i]) == i + 1:
        count += 1

print(count)
