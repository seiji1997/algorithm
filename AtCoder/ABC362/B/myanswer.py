# This is the myanswer.py for problem B in ABC362
def check_triangle(Xa, Ya, Xb, Yb, Xc, Yc):
    AB = (Xa - Xb)**2 + (Yb - Ya)**2
    BC = (Xb - Xc)**2 + (Yc - Yb)**2
    CA = (Xc - Xa)**2 + (Ya - Yc)**2

    if AB + BC == CA or BC + CA == AB or CA + AB == BC:
        return "Yes"
    else:
        return "No"

if __name__ == "__main__":
    Xa, Ya = map(int, input().split())
    Xb, Yb = map(int, input().split())
    Xc, Yc = map(int, input().split())
    
    result = check_triangle(Xa, Ya, Xb, Yb, Xc, Yc)
    print(result)
