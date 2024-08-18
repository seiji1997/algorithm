# This is the myanswer.py for problem B in ABC367
X = input().strip()
X_float = float(X)
formatted_X = ("{:.3f}".format(X_float)).rstrip("0").rstrip(".")
print(formatted_X)
