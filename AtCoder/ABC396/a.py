def main():
    import sys

    data = sys.stdin.read().split()

    n = int(data[0])
    arr = list(map(int, data[1:]))

    count = 1
    for i in range(1, n):
        if arr[i] == arr[i - 1]:
            count += 1
            if count >= 3:
                print("Yes")
                return
        else:
            count = 1
    print("No")


if __name__ == "__main__":
    main()
