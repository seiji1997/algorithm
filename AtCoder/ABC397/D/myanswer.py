# This is the myanswer.py for problem D in ABC397
import sys
import math


def is_perfect_square(n):
    """
    与えられた整数 n が完全平方数であれば、その平方根（整数）を返す。
    そうでなければ None を返す。

    Parameters:
        n (int): チェック対象の整数。負の場合は None を返す。

    Returns:
        int or None: n の平方根（整数）または None
    """
    if n < 0:
        return None
    r = math.isqrt(n)
    return r if r * r == n else None


def find_solution(N):
    """
    与えられた正整数 N に対して、正整数 x, y が存在し x^3 - y^3 = N を満たすか調べる。
    存在する場合はその一例として (x, y) を返す。存在しなければ None を返す。

    方程式は (x - y)(x^2 + x*y + y^2) = N と因数分解できるので、
    ここでは x - y = d とおき、x = y + d と置くことで
        (y + d)^3 - y^3 = 3*d*y^2 + 3*d^2*y + d^3 = N
    と変形できる。d が N の約数であることに注目し、d に対して y の2次方程式
        3*y^2 + 3*d*y + d^2 = N / d
    を解くことで候補を探索する。

    Parameters:
        N (int): 方程式の定数項（1 ≤ N ≤ 10^18）

    Returns:
        tuple or None: 条件を満たす (x, y) の組（x, y は正整数）または解が存在しない場合 None
    """
    # d^3 <= 4N より、d の上限は (4N)^(1/3) となる（安全のため+2）
    limit = int((4 * N) ** (1 / 3)) + 2
    for d in range(1, limit):
        if N % d != 0:
            continue
        q = N // d
        # 2次方程式: 3*y^2 + 3*d*y + (d^2 - q) = 0 の判別式
        delta = 12 * q - 3 * d * d  # 計算上は 9*d^2 - 12*(d^2 - q) と同値
        if delta < 0:
            continue
        r = is_perfect_square(delta)
        if r is None:
            continue
        # y = (-3*d + sqrt(delta)) / 6
        if (-3 * d + r) % 6 != 0:
            continue
        y = (-3 * d + r) // 6
        if y <= 0:
            continue
        x = y + d
        # 最終確認: x^3 - y^3 が N に一致するか
        if x**3 - y**3 == N:
            return (x, y)
    return None


def main():
    """
    標準入力から整数 N を読み込み、x^3 - y^3 = N を満たす正整数 (x, y) が存在するか判定する。
    存在すれば x と y を空白区切りで出力し、存在しなければ -1 を出力する。
    """
    # 入力の読み込み
    input_line = sys.stdin.readline().strip()
    if not input_line:
        return
    N = int(input_line)

    # 解の探索
    result = find_solution(N)

    # 結果の出力
    if result is None:
        print(-1)
    else:
        x, y = result
        print(f"{x} {y}")


if __name__ == "__main__":
    main()
