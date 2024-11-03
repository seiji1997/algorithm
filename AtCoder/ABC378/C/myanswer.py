# This is the myanswer.py for problem C in ABC378


def find_previous_positions(n, a):
    b = [-1] * n
    last_seen = {}

    for i in range(n):
        current_value = a[i]
        if current_value in last_seen:
            b[i] = last_seen[current_value] + 1
        last_seen[current_value] = i

    return b


n = int(input().strip())
a = list(map(int, input().strip().split()))

b = find_previous_positions(n, a)
print(" ".join(map(str, b)))
