# This is the myanswer.py for problem B in ABC378
def next_collection_day(d, q, r):
    if d % q <= r:
        return d + (r - (d % q))
    else:
        return d + (q - (d % q) + r)


N = int(input().strip())
garbage_rules = []
for _ in range(N):
    q, r = map(int, input().strip().split())
    garbage_rules.append((q, r))

Q = int(input().strip())
queries = []
for _ in range(Q):
    t, d = map(int, input().strip().split())
    queries.append((t - 1, d))

results = []
for t, d in queries:
    q, r = garbage_rules[t]
    results.append(next_collection_day(d, q, r))

for result in results:
    print(result)
