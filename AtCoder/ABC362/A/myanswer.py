# This is the myanswer.py for problem A in ABC362
R, G, B = map(int, input().split())
C = input()

if C == "Red":
    print(min(G, B))
elif C == "Green":
    print(min(R, B))
elif C == "Blue":
    print(min(R, G))
else:
    print("Invalid color")

# code golf
R, G, B = map(int, input().split())
C = input()
print(min(G, B) if C == "Red" else min(R, B) if C == "Green" else min(R, G))
