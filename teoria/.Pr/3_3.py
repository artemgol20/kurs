from itertools import chain, combinations

# Исходные данные
objects = {'1', '2', '3', '4'}
attributes = {'a', 'b', 'c', 'd'}

# Таблица инцидентности
context = {
    '1': {'a', 'd'},
    '2': {'b', 'c'},
    '3': {'a', 'c'},
    '4': {'b', 'c'}
}

# Функция нахождения всех подмножеств
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

# Поиск всех концептов
def find_concepts(objects, attributes, context):
    concepts = []
    for A in powerset(objects):
        if not A:
            continue
        B = set.intersection(*(context[obj] for obj in A)) if A else attributes
        A_prime = {obj for obj in objects if context[obj].issuperset(B)}
        if set(A) == A_prime:
            concepts.append((set(A), B))
    return concepts

# Построение решетки
def build_lattice(concepts):
    edges = []
    for A1, B1 in concepts:
        for A2, B2 in concepts:
            if A1 < A2 and B2 < B1:  # A1 ⊆ A2 и B2 ⊆ B1
                if not any(A1 < Am < A2 and B2 < Bm < B1 for Am, Bm in concepts):
                    edges.append((A1, A2))
    return edges

# Основной алгоритм
concepts = find_concepts(objects, attributes, context)
edges = build_lattice(concepts)

# Вывод концептов
print("\nКонцепты:")
for i, (A, B) in enumerate(concepts):
    print(f"{i}: Объекты: {A}, Атрибуты: {B}")

# Вывод рёбер
print("\nРёбра решётки:")
for parent, child in edges:
    print(f"{concepts.index((parent, next(B for A, B in concepts if A == parent)))} → "
          f"{concepts.index((child, next(B for A, B in concepts if A == child)))}")
