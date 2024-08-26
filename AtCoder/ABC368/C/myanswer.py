# This is the myanswer.py for problem C in ABC368
def calculate_T(N, H):
    T = 0  
    for i in range(N):
        while H[i] > 0:
            if H[i] >= 5:
                steps_of_5 = H[i] // 5
                H[i] -= steps_of_5 * 5
                T += steps_of_5 * 3 
            else:
                T += 1
                if T % 3 == 0:
                    H[i] -= 3
                else:
                    H[i] -= 1

    return T

N = int(input())
H = list(map(int, input().split()))
print(calculate_T(N, H))

