# This is the myanswer.py for problem B in ABC373
def min_distance(S: str) -> int:
    key_positions = {char: idx for idx, char in enumerate(S, 1)}

    current_position = key_positions["A"]
    total_distance = 0

    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        next_position = key_positions[char]
        total_distance += abs(next_position - current_position)
        current_position = next_position

    return total_distance


S = input()

print(min_distance(S))
