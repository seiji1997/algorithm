#!/usr/bin/env python3
# This is the main.py for problem A in ABC366
def calculate_vote_count(N):
    return (N // 2) + 1

def determine_winner(T, A, vote_count):
    return "Yes" if T >= vote_count or A >= vote_count else "No"

def main():
    N, T, A = map(int, input().split())
    vote_count = calculate_vote_count(N)
    result = determine_winner(T, A, vote_count)
    print(result)

if __name__ == "__main__":
    main()
