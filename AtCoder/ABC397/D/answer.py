import sys
import math


def is_perfect_square(n):
    if n < 0:
        return None
    r = math.isqrt(n)
    return r if r * r == n else None


def find_solution(N):
    limit = int((4 * N) ** (1 / 3)) + 2
    for d in range(1, limit):
        if N % d != 0:
            continue
        q = N // d
        delta = 12 * q - 3 * d * d
        if delta < 0:
            continue
        r = is_perfect_square(delta)
        if r is None:
            continue
        if (-3 * d + r) % 6 != 0:
            continue
        y = (-3 * d + r) // 6
        if y <= 0:
            continue
        x = y + d
        if x**3 - y**3 == N:
            return (x, y)
    return None


def main():
    input_line = sys.stdin.readline().strip()
    if not input_line:
        return
    N = int(input_line)
    result = find_solution(N)
    if result is None:
        print(-1)
    else:
        x, y = result
        print(f"{x} {y}")


if __name__ == "__main__":
    main()
