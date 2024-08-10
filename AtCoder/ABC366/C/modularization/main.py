#!/usr/bin/env python3
# This is the main.py for problem C in ABC366
import sys
from ball_counter import process_queries

def main():
    input = sys.stdin.read
    data = input().splitlines()
    queries = data[1:] 
    results = process_queries(queries)
    sys.stdout.write("\n".join(results) + "\n")

if __name__ == "__main__":
    main()
