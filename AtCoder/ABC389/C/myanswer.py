import sys


def solve():
    data = sys.stdin.read().split()
    Q = int(data[0])
    heads, lengths = [], []
    front = 0
    offset = 0
    ans = []
    idx = 1

    for _ in range(Q):
        t = int(data[idx])
        idx += 1

        if t == 1:
            l = int(data[idx])
            idx += 1
            if heads:
                heads.append(heads[-1] + lengths[-1])
            else:
                heads.append(0)
            lengths.append(l)

        elif t == 2:
            offset -= lengths[front]
            front += 1

        else:
            k = int(data[idx])
            idx += 1
            ans.append(str(offset + heads[front + k - 1]))

    print("\n".join(ans))


if __name__ == "__main__":
    solve()
