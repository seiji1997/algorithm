# This is the myanswer.py for problem B in ABC384
def solve():
    first_line = input().strip().split()
    N, R = int(first_line[0]), int(first_line[1])
    DIV1_MIN, DIV1_MAX = 1600, 2799
    DIV2_MIN, DIV2_MAX = 1200, 2399

    for _ in range(N):
        line = input().strip().split()
        division, rating_change = int(line[0]), int(line[1])
        current_rating = R

        def is_update_target(div, rating):
            if div == 1:
                return DIV1_MIN <= rating <= DIV1_MAX
            else:  # div == 2
                return DIV2_MIN <= rating <= DIV2_MAX

        if is_update_target(division, current_rating):
            R = current_rating + rating_change

    print(R)


if __name__ == "__main__":
    solve()
