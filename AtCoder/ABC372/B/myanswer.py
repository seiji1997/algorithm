# This is the myanswer.py for problem B in ABC372
"""条件に合致する N と A の組み合わせを求める
M が与えられるので、M を満たす N と非負整数列 A を見つける
まず、N の最大値は20と仮定、その範囲内で Ai を設定
各 Ai は M // 3 の範囲で決定し、M が減少していくのを確認
結果として N と A を出力
"""


def find_N_and_A(M):
    max_N = 20  # Nの最大値は20
    A = [0] * max_N  # Aの初期化

    # 3Aiの和がMになるようにAiを決定
    for i in range(max_N):
        Ai = min(M // 3, 9)  # Aiは0〜9の範囲で設定
        A[i] = Ai
        M -= 3 * Ai  # Mを更新

    # 残ったMを調整（0にする）
    i = 0
    while M > 0:
        A[i] += 1
        M -= 3
        i += 1

    # Nを求める。不要な0を取り除くため、末尾の0を削除する
    while A[-1] == 0:
        A.pop()

    N = len(A)
    # 結果を出力
    print(N)
    print(" ".join(map(str, A)))


# 入力
M = int(input())

# 結果を出力
find_N_and_A(M)
