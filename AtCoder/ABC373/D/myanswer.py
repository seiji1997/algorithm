# This is the myanswer.py for problem D in ABC373
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.diff_weight = [0] * n  # 根からの相対的な重み

    def find(self, x):
        if self.parent[x] == x:
            return x
        else:
            root = self.find(self.parent[x])
            self.diff_weight[x] += self.diff_weight[self.parent[x]]  # 相対重みを更新
            self.parent[x] = root
            return root

    def unite(self, x, y, weight):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            self.diff_weight[root_x] = (
                self.diff_weight[y] - self.diff_weight[x] + weight
            )
        else:
            self.parent[root_y] = root_x
            self.diff_weight[root_y] = (
                self.diff_weight[x] - self.diff_weight[y] - weight
            )
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def weight(self, x):
        self.find(x)
        return self.diff_weight[x]


def solve():
    N, M = map(int, input().split())
    uf = UnionFind(N)

    for _ in range(M):
        u, v, w = map(int, input().split())
        uf.unite(u - 1, v - 1, w)

    result = [uf.weight(i) for i in range(N)]
    print(" ".join(map(str, result)))


solve()
