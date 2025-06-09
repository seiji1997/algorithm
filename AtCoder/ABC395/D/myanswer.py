import sys

input = sys.stdin.readline
N, Q = map(int, input().split())

A = [0] * (N + 1)
B = [0] * (N + 1)
pos = [0] * (N + 1)
ans = []


def move_pigeon(line):
    a = int(line[1])
    b = int(line[2])
    pos[a] = B[b] if B[b] != 0 else b


def swap_nests(line):
    a = int(line[1])
    b = int(line[2])
    La = B[a] if B[a] != 0 else a
    Lb = B[b] if B[b] != 0 else b
    ALa = A[La] if A[La] != 0 else La
    ALb = A[Lb] if A[Lb] != 0 else Lb
    A[La], A[Lb] = ALb, ALa
    B[ALb], B[ALa] = La, Lb


def report_pigeon(line):
    a = int(line[1])
    la = pos[a] if pos[a] != 0 else a
    nest = A[la] if A[la] != 0 else la
    ans.append(str(nest))


for _ in range(Q):
    line = input().split()
    t = int(line[0])
    match t:
        case 1:
            move_pigeon(line)
        case 2:
            swap_nests(line)
        case 3:
            report_pigeon(line)

print("\n".join(ans))
