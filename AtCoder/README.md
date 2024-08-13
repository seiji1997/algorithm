# Learning algorithm
### **Competitive programming**
- AtCoder([https://atcoder.jp/](https://atcoder.jp/))

If I were to give a rough evaluation without fear of misunderstanding, it would be as follows:

- Gray: Anyone can reach this rank just by participating, so there’s no guarantee beyond enthusiasm.
- Brown: If you're a student at the brown level, you're considered talented, but as an engineer, it might be a bit lacking. If a contracted engineer is brown, you can feel reassured.
- Green: For most companies, this level is sufficient in terms of algorithm skills. While it may not be a top rank on AtCoder, it would receive the highest rating on other evaluation sites.
- Cyan: This level indicates a solid foundation in algorithm processing skills.
- Blue and above: This level is rare enough that even some publicly traded IT companies may not have a single employee at this rank.
- Yellow: From this rank onward, we're talking about "monsters." You can think of them as machines that solve competitive programming problems.
- Orange: This level is truly exceptional, with an extraordinary intellect.
- Red: This rank involves being invited to world competitions and such.

You can think of it in these terms. If you want a more detailed explanation, please read the sections below.

### level

#### Gray (E Rank Rating ~399)
The condition for becoming gray is simply participating in AtCoder once. <br>
Therefore, AtCoder does not guarantee any skill level at this rank. <br>
If you're gray, please participate in more contests and work on improving your skills.<br>
If your rating is above 200, you would rank quite high on other sites. <br>
We are considering setting up a system on AtCoderJobs to evaluate skills.<br>

#### Brown (D Rank Rating 400~799 Top 50%)
To become brown, you need a rating of 400 or more.<br>
While the skill level at this rank is not particularly high within AtCoder, it does show a strong commitment. <br>
On other job search sites, even this rating can place you in the top 1-2%, so it is generally considered a high level.<br>
If an information science student is brown, they give the impression of being diligent.<br> 
If a contracted programmer is brown, you can feel relatively reassured.<br>
However, in terms of algorithm skills, it might still be lacking.<br>
The technical guarantees at this rank are:
- Basic operations like standard input/output, if statements, and for loops are mastered.
- They can correctly understand problem statements and implement them according to specifications without considering computational complexity.

However, to reach the brown level, one must also have:
- The mathematical ability and logical thinking required to enter a science department at a university.
- Knowledge of standard algorithms and the ability to solve typical problems like exhaustive searches or simple dynamic programming.
- Fast and accurate coding skills for simple problems.
- All brown-level programmers can instantly solve coding tests like FizzBuzz.

#### Green (C Rank R800~1199 Top 30%)
If you reach the green level, you can be considered someone who is seriously engaged in competitive programming.<br>
The required level is not low, and you can’t reach this level by luck alone. In other algorithm assessment services, this would rank in the top 1%.<br>
Technically, green-level programmers can:
- Perform operations on 2D arrays and implement depth-first and breadth-first search using queues or recursion.
- Begin to tackle problems that require optimization of computational complexity, such as basic dynamic programming.

#### Cyan (B Rank R1200~1599 Top 15%)
Cyan is a very high level, and many programmers considered “extremely talented” in companies are at least this rank.<br>
Those who excel in mathematics often move up to the next level, blue.<br>
In more than half of IT companies, this level could be considered the peak for algorithm skills. <br>
For companies that do not require much algorithmic ability, moving beyond this level may not contribute significantly to practical work.<br>
Technically, cyan-level programmers:
- Have a strong intuition for computational complexity and can implement complex processes with ease.
- Can perform depth-first and breadth-first searches, permutations, and exhaustive pattern enumerations. 
- They can also begin to optimize these with dynamic programming or memoization.
- Can apply techniques like greedy algorithms, dynamic programming, two-pointer techniques, and binary search to improve computational efficiency.
- Are skilled in data structures like cumulative sums and Union-Find (Disjoint Set outside of competitive programming).
- Can handle basic graph algorithms like Dijkstra’s algorithm, Warshall-Floyd, and Kruskal’s algorithm, and apply appropriate processing to tree and graph structures.
- Possess a solid foundation in mathematics, including knowledge of prime numbers and their properties, primality testing, enumeration of divisors, least common multiples, greatest common divisors, and combinatorial calculations common in competitive programming.

As you can see, the skill requirements jump significantly when reaching the cyan level.Gray (E Rank Rating ~399)<br>
The condition for becoming gray is simply participating in AtCoder once.<br>
Therefore, AtCoder does not guarantee any skill level at this rank. If you're gray, please participate in more contests and work on improving your skills.<br>
If your rating is above 200, you would rank quite high on other sites. We are considering setting up a system on AtCoderJobs to evaluate skills.

##### 20min~1hで解きたい
https://atcoder.jp/contests/aising2019/tasks/aising2019_c

```python
from sys import setrecursionlimit
from collections import defaultdict

# Set recursion limit to handle deep recursion
setrecursionlimit(10**6)

# Input reading
H, W = map(int, input().split())
grid = [input() for _ in range(H)]

# Directions for moving (down, up, right, left)
directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# Visited flag
visited = [[False] * W for _ in range(H)]

# DFS to count connected components
def dfs(x, y):
    visited[y][x] = True
    black, white = 0, 0
    stack = [(x, y)]

    # Count initial cell
    if grid[y][x] == "#":
        black += 1
    else:
        white += 1

    while stack:
        cx, cy = stack.pop()

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy

            # Check bounds and if the cell is unvisited and alternating in color
            if 0 <= nx < W and 0 <= ny < H and not visited[ny][nx]:
                if grid[ny][nx] != grid[cy][cx]:
                    visited[ny][nx] = True
                    stack.append((nx, ny))
                    if grid[ny][nx] == "#":
                        black += 1
                    else:
                        white += 1

    return black, white

# Calculate the answer
ans = 0
for y in range(H):
    for x in range(W):
        if not visited[y][x]:
            b, w = dfs(x, y)
            ans += b * w

print(ans)
```



##### 1h で解きたい
https://atcoder.jp/contests/arc100/tasks/arc100_b

```python
from bisect import bisect_left
from itertools import accumulate

def solve_problem(n, A):
    A = [0] + A  # Prefix sum array
    for i in range(n):
        A[i + 1] += A[i]
    
    ans = float('inf')  # Initialize with infinity

    for i in range(2, n - 1):
        x = []

        # Determine the best left split
        l = bisect_left(A, A[i] // 2)
        if A[l] - A[0] < A[i] - A[l - 1]:
            x += [A[l] - A[0], A[i] - A[l]]
        else:
            x += [A[l - 1] - A[0], A[i] - A[l - 1]]

        # Determine the best right split
        r = bisect_left(A, A[i] + (A[n] - A[i]) // 2)
        if A[r] - A[i] < A[n] - A[r - 1]:
            x += [A[r] - A[i], A[n] - A[r]]
        else:
            x += [A[r - 1] - A[i], A[n] - A[r - 1]]
        
        # Update the answer with the minimal difference
        ans = min(ans, max(x) - min(x))
    
    return ans

# Input
n = int(input())
A = list(map(int, input().split()))

# Output the result
print(solve_problem(n, A))
```
