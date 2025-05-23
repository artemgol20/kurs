def relation(a, b):
    return b % a == 0 if a != 0 else False

def build_hasse_diagram(elements):
    levels = []
    remaining = set(elements)
    
    # Разбиваем элементы на уровни 
    while remaining:
        min_elements = {x for x in remaining 
                       if not any(relation(y, x) and y != x for y in remaining)}
        levels.append(min_elements)
        remaining -= min_elements
    
    # Находим рёбра 
    edges = []
    for i in range(1, len(levels)):
        upper = levels[i]
        lower = levels[i - 1]
        for u in upper:
            for l in lower:
                if relation(l, u):
                    # Проверяем, что нет промежуточного элемента
                    is_cover = True
                    for m in remaining.union(upper).union(lower) - {u, l}:
                        if relation(l, m) and relation(m, u):
                            is_cover = False
                            break
                    if is_cover:
                        edges.append((l, u))
    
    return levels, edges


# Пример использования:
A = {2, 3, 5, 6, 10, 15, 30}

levels, edges = build_hasse_diagram(A)

print("Уровни диаграммы Хассе:")
for i, level in enumerate(levels, 1):
    print(f"Уровень {i}: {level}")

print("\nРёбра (покрытия):")
for edge in edges:
    print(f"{edge[0]} → {edge[1]}")