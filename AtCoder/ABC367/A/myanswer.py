# This is the myanswer.py for problem A in ABC367
A, B, C = map(int, input().split())

def check_time(A, B, C):
    if B < C:
        if B <= A < C:
            return "No"
        else:
            return "Yes"
    else:
        if A >= B or A < C:
            return "No"
        else:
            return "Yes"
        
print(check_time(A, B, C))
