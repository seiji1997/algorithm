def main():
    import sys

    input = sys.stdin.readline

    Q = int(input())
    stack = [0] * 100

    for _ in range(Q):
        query = input().split()
        if query[0] == "1":
            x = int(query[1])
            stack.append(x)
        elif query[0] == "2":
            print(stack.pop())


if __name__ == "__main__":
    main()
