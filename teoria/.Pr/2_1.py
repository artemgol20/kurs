import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

W = ["baa", "aba", "abb", "bba", "bbb"]
n = len(W)

def compare_letterwise(word1, word2):
    return all(a <= b for a, b in zip(word1, word2))

def compare_lexicographically(word1, word2):
    return word1 <= word2

def build_relation_matrix(W, compare_func):
    matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if compare_func(W[i], W[j]):
                matrix[i][j] = 1
    return matrix

def draw_graph(matrix, W, title, color="lightblue"):
    G = nx.DiGraph()
    for word in W:
        G.add_node(word)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 1 and i != j:
                G.add_edge(W[i], W[j])
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color=color,
            font_size=15, font_weight='bold', arrows=True)
    plt.title(title)
    plt.show()

def hasse_diagram(matrix, W):
    G_hasse = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 1 and i != j:
                if not any(matrix[i][k] == 1 and matrix[k][j] == 1 for k in range(n) if k != i and k != j):
                    G_hasse.add_edge(W[i], W[j])
    return G_hasse

def draw_hasse(matrix, W, title, color="orange"):
    H = hasse_diagram(matrix, W)
    plt.figure(figsize=(8, 6))
    pos_hasse = nx.spring_layout(H)
    nx.draw(H, pos_hasse, with_labels=True, node_size=2000, node_color=color,
            font_size=15, font_weight='bold', arrows=True)
    plt.title(title)
    plt.show()

# Побуквенное упорядочение
matrix_letterwise = build_relation_matrix(W, compare_letterwise)
print("Матрица сравнения для побуквенного упорядочения:")
print(matrix_letterwise)
draw_graph(matrix_letterwise, W, "Граф побуквенного упорядочения")
draw_hasse(matrix_letterwise, W, "Диаграмма Хассе побуквенного упорядочения")

# Лексикографическое упорядочение
matrix_lexicographic = build_relation_matrix(W, compare_lexicographically)
print("\nМатрица сравнения для лексикографического упорядочения:")
print(matrix_lexicographic)
draw_graph(matrix_lexicographic, W, "Граф лексикографического упорядочения")
draw_hasse(matrix_lexicographic, W, "Диаграмма Хассе лексикографического упорядочения")
