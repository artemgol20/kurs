import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

W = ['baa','aba','abb','bba','bbb']
n = len(W)

def compare_letterwise(word1, word2):
    return all(a <= b for a, b in zip(word1, word2))

matrix_letterwise = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        if compare_letterwise(W[i], W[j]):
            matrix_letterwise[i][j] = 1

print("Матрица сравнения для побуквенного упорядочения")
print(matrix_letterwise)

G_letterwise = nx.DiGraph()
for word in W:
    G_letterwise.add_node(word)
for i in range(n):
    for j in range(n):
        if matrix_letterwise[i][j] == 1 and i != j:
            G_letterwise.add_edge(W[i], W[j])

plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G_letterwise)
nx.draw(G_letterwise, pos, with_labels=True, node_size=2000,
        node_color='lightblue', font_size=15, font_weight='bold',
        arrows=True)
plt.title("Граф побуквенного упорядочения")
plt.show()

def hasse_diagram(matrix, W):
    G_hasse = nx.DiGraph()
    n = len(W)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 1 and i != j:
                if not any(matrix[i][k] == 1 and matrix[k][j] == 1 for k in range(n) if k != i and k != j):
                    G_hasse.add_edge(W[i], W[j])
    return G_hasse

H_letterwise = hasse_diagram(matrix_letterwise, W)

plt.figure(figsize=(8, 6))
pos_hasse = nx.spring_layout(H_letterwise)
nx.draw(H_letterwise, pos_hasse, with_labels=True, node_size=2000,
        node_color='orange', font_size=15, font_weight='bold', arrows=True)
plt.title("Диаграмма Хассе побуквенного упорядочения")
plt.show()

def compare_lexicographically(word1, word2):
    return word1 <= word2

matrix_lexicographic = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        if compare_lexicographically(W[i], W[j]):
            matrix_lexicographic[i][j] = 1

print("\nМатрица сравнения для лексикографического упорядочения:")
print(matrix_lexicographic)

G_lexicographic = nx.DiGraph()
for word in W:
    G_lexicographic.add_node(word)
for i in range(n):
    for j in range(n):
        if matrix_lexicographic[i][j] == 1 and i != j:
            G_lexicographic.add_edge(W[i], W[j])

plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G_lexicographic)
nx.draw(G_lexicographic, pos, with_labels=True, node_size=2000,
        node_color='lightblue', font_size=15, font_weight='bold',
        arrows=True)
plt.title("Граф лексикографического упорядочения")
plt.show()

H_lexicographic = hasse_diagram(matrix_lexicographic, W)

plt.figure(figsize=(8, 6))
pos_hasse = nx.spring_layout(H_lexicographic)
nx.draw(H_lexicographic, pos_hasse, with_labels=True, node_size=2000,
        node_color='orange', font_size=15, font_weight='bold', arrows=True)
plt.title("Диаграмма Хассе лексикографического упорядочения")
plt.show()
