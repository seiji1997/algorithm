import sys


def read_input():
    data = sys.stdin.read().strip().split()
    it = iter(data)
    N = int(next(it))
    M = int(next(it))
    B = [int(next(it)) for _ in range(N)]
    W = [int(next(it)) for _ in range(M)]
    return N, M, B, W


def compute_sorted_prefix(arr):
    sorted_arr = sorted(arr, reverse=True)
    prefix = [0]
    for a in sorted_arr:
        prefix.append(prefix[-1] + a)
    return prefix


def compute_prefix_max(prefix):
    prefix_max = []
    current_max = float("-inf")
    for x in prefix:
        current_max = max(current_max, x)
        prefix_max.append(current_max)
    return prefix_max


def calculate_max_sum(prefix_B, prefix_W_max, M):
    ans = 0
    for i in range(len(prefix_B)):
        j = min(i, M)
        total = prefix_B[i] + prefix_W_max[j]
        ans = max(ans, total)
    return ans if ans > 0 else 0


def main():
    _, M, B, W = read_input()
    prefix_B = compute_sorted_prefix(B)
    prefix_W = compute_sorted_prefix(W)
    prefix_W_max = compute_prefix_max(prefix_W)
    result = calculate_max_sum(prefix_B, prefix_W_max, M)
    print(result)


if __name__ == "__main__":
    main()
