import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

M = [3,7,21,33,35,63]
n = len(M)

div_matrix = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        if M[j] % M[i] == 0:
            div_matrix[i][j] = 1

print("Матрица отношений делимости:")
print(div_matrix)

min_elements = [M[i] for i in range(n) if all(div_matrix[j][i] == 0 for j in range(n) if i != j)]
max_elements = [M[i] for i in range(n) if all(div_matrix[i][j] == 0 for j in range(n) if i != j)]

print(f"Минимальные элементы: {min_elements}")
print(f"Максимальные элементы: {max_elements}")

G = nx.DiGraph()
for number in M:
    G.add_node(number)
for i in range(n):
    for j in range(n):
        if div_matrix[i][j] == 1 and i != j:
            G.add_edge(M[i], M[j])

plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=15, font_weight='bold', arrows=True)
plt.title("Граф делимости")
plt.show()

def hasse_diagram(M):
    G_hasse = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if div_matrix[i][j] == 1 and i != j:
                if not any(div_matrix[i][k] == 1 and div_matrix[k][j] == 1 for k in range(n) if k != i and k != j):
                    G_hasse.add_edge(M[i], M[j])
    return G_hasse

H = hasse_diagram(M)

plt.figure(figsize=(8, 6))
pos_hasse = nx.spring_layout(H)
nx.draw(H, pos_hasse, with_labels=True, node_size=2000, node_color='lightblue', font_size=15, font_weight='bold', arrows=True)
plt.title("Диаграмма Хассе")
plt.show()