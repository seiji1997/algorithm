from collections import defaultdict

def one(ball_count, x):
    ball_count[x] += 1

def two(ball_count, x):
    if ball_count[x] == 1:
        del ball_count[x]
    else:
        ball_count[x] -= 1

def three(ball_count):
    return len(ball_count)

def handle_query(query, ball_count):
    parts = query.split()
    query_type = int(parts[0])
    
    if query_type == 1:
        x = int(parts[1])
        one(ball_count, x)
    elif query_type == 2:
        x = int(parts[1])
        two(ball_count, x)
    elif query_type == 3:
        return three(ball_count)
    return None

def process_queries(queries):
    ball_count = defaultdict(int)
    results = []
    
    for query in queries:
        result = handle_query(query, ball_count)
        if result is not None:
            results.append(str(result))
    
    return results
