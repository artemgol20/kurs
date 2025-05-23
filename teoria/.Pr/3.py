import networkx as nx
import matplotlib.pyplot as plt

# Определяем бинарную матрицу отношений
context_data = [
    [1, 0, 0, 1],
    [0, 1, 1, 0],
    [1,0, 1, 0],
    [0, 1, 1, 0]
]

objects = ['1', '2', '3', '4']  # Объекты G
attributes = ['a', 'b', 'c', 'd']  # Атрибуты M

def compute_concepts(objects, attributes, context_data):
    concepts = []
    for i in range(1 << len(objects)):
        extent = {objects[j] for j in range(len(objects)) if (i & (1 << j))}
        if not extent:
            continue
        intent = {attributes[k] for k in range(len(attributes)) if all(context_data[j][k] for j in range(len(objects)) if objects[j] in extent)}
        concepts.append((extent, intent))
    return concepts

def build_lattice(concepts):
    G = nx.DiGraph()
    nodes = {str(extent) + " | " + str(intent): (extent, intent) for extent, intent in concepts}
    for parent in concepts:
        for child in concepts:
            if parent != child and parent[0] > child[0] and all(not (parent[0] > other[0] > child[0]) for other in concepts):
                G.add_edge(str(parent[0]) + " | " + str(parent[1]), str(child[0]) + " | " + str(child[1]))
    return G

concepts = compute_concepts(objects, attributes, context_data)
lattice = build_lattice(concepts)

# Рисуем граф решетки концептов
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(lattice)
nx.draw(lattice, pos, with_labels=True, node_size=2000, node_color='lightblue', 
        font_size=10, font_weight='bold', arrows=True)
plt.title("Решетка концептов")
plt.show()
