# This is the myanswer.py for problem A in ABC371

SAB, SAC, SBC = input().split()

if SAB == "<" and SAC == "<" and SBC == "<":
    print("B")
elif SAB == "<" and SAC == "<" and SBC == ">":
    print("C")
elif SAB == "<" and SAC == ">" and SBC == "<":
    print("C")
elif SAB == "<" and SAC == ">" and SBC == ">":
    print("A")
elif SAB == ">" and SAC == "<" and SBC == "<":
    print("A")
elif SAB == ">" and SAC == "<" and SBC == ">":
    print("B")
elif SAB == ">" and SAC == ">" and SBC == "<":
    print("A")
elif SAB == ">" and SAC == ">" and SBC == ">":
    print("B")
