# This is the myanswer.py for problem D in ABC367
"""
acc: 累積和を保持するリスト
mod_count: モジュロのカウントを保持するリスト
"""

def count_pairs(N, M, A):
    # 累積和の計算
    acc = [0] * (2 * N + 1)
    for i in range(2 * N):
        acc[i + 1] = (acc[i] + A[i % N]) % M
    
    # 最初のN個分の累積和のモジュロをカウント
    mod_count = [0] * M
    for i in range(N):
        mod_count[acc[i]] += 1
    
    # ペア数のカウント
    result = 0
    for i in range(N):
        mod_count[acc[i]] -= 1  # 現在のモジュロのカウントを減らす
        result += mod_count[acc[i]]  # 同じモジュロ値を持つペアの数を加算
        mod_count[acc[i + N]] += 1  # 一周後の累積和を考慮してカウントを増やす
    
    return result


def main():
    N, M = map(int, input().split())
    A = list(map(int, input().split()))
    print(count_pairs(N, M, A))


if __name__ == '__main__':
    main()