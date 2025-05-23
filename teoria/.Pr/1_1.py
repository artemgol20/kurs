from collections import deque

def topological_sort_matrix(M):
    n = len(M)
    # Преобразование матрицы в список смежности
    graph = {i: [] for i in range(n)}
    in_degree = [0] * n
    
    for i in range(n):
        for j in range(n):
            if M[i][j] == 1:
                graph[i].append(j)
                in_degree[j] += 1
    
    # Алгоритм Кана
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == n else None
M = [
    [0, 1, 0],  # 0 → 1
    [0, 0, 1],  # 1 → 2
    [0, 0, 0]   # 2
]
print(topological_sort_matrix(M))  # Возможные выводы: [0, 1, 2]
