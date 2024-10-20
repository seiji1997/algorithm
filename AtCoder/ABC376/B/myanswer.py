def num_move(n, from_, to, ng):
    # from_ と to を常に from_ <= to になるように入れ替える
    if from_ > to:
        from_, to = to, from_
    # ng が from_ と to の間にある場合
    if from_ < ng < to:
        return n + from_ - to  # 円環をぐるっと回る移動
    else:
        return to - from_  # 通常の移動距離


# 入力の読み込み
n, q = map(int, input().split())
l, r = 1, 2  # 左手は 1、右手は 2 に初期設定
ans = 0

# 各指示に従う処理
for _ in range(q):
    h, t = input().split()  # h は手の種類、t は目的地
    t = int(t)
    if h == "L":
        # 左手を移動
        ans += num_move(n, l, t, r)  # 右手は ng の位置として渡す
        l = t  # 左手の位置を更新
    else:
        # 右手を移動
        ans += num_move(n, r, t, l)  # 左手は ng の位置として渡す
        r = t  # 右手の位置を更新

# 結果の出力
print(ans)


# another answer
# N,Q=map(int,input().split())
# L,R=1,2
# ans=0
# for _ in range(Q):
#   H,T=input().split()
#   T=int(T)
#   if H=='L':
#     to=(T-L)%N
#     ng=(R-L)%N
#     if ng<to: ans+=N-to
#     else: ans+=to
#     L=T
#   else:
#     to=(T-R)%N
#     ng=(L-R)%N
#     if ng<to: ans+=N-to
#     else: ans+=to
#     R=T

# print(ans)
