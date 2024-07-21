# This is the myanswer.py for problem A in ABC363
R = int(input())

if 1 <= R <= 99:
    R -= 100
    print(abs(R))
elif 100 <= R <= 199:
    R -= 200
    print(abs(R))
elif 200 <= R <= 299:
    R -= 300
    print(abs(R))
else:
    ("Invalid error")


# --------------------------- 
R = int(input())

if 1 <= R <= 99:
    print(100 - R)
elif 100 <= R <= 199:
    print(200 - R)
elif 200 <= R <= 299:
    print(300 - R)
else:
    print("Invalid error")
