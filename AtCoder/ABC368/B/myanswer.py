# This is the myanswer.py for problem B in ABC368
def operations(N, A):
    operation = 0

    while sum(1 for x in A if x > 0) > 1:
        A.sort(reverse=True)
        if A[0] > 0:
            A[0] -= 1
        if A[1] > 0:
            A[1] -= 1
        operation += 1
    return operation

N = int(input())
A = list(map(int, input().split()))

result = operations(N, A)
print(result)