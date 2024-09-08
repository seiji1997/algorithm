def find_element(N, A):
    result = 1

    for i in range(2, N + 1):
        if i >= result:
            result = A[i - 1][result - 1]
        else:
            result = A[result - 1][i - 1]

    return result


N = int(input())
A = []

for i in range(N):
    A.append(list(map(int, input().split())))

print(find_element(N, A))
