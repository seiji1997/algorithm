# This is the myanswer.py for problem C in ABC376
def min_box_size(N, toys, boxes):
    toys.sort()
    boxes.sort()

    def can_fit(x):
        new_boxes = boxes + [x]
        new_boxes.sort()

        for i in range(N):
            if toys[i] > new_boxes[i]:
                return False
        return True

    low, high = 1, max(toys)
    result = -1

    while low <= high:
        mid = (low + high) // 2
        if can_fit(mid):
            result = mid
            high = mid - 1
        else:
            low = mid + 1
    return result


N = int(input())
toys = list(map(int, input().split()))
boxes = list(map(int, input().split()))

print(min_box_size(N, toys, boxes))
