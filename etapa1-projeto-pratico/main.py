#=======================================================
#   Authors:
#       . Fábio Damas Valim (202410372)
#       . Guilherme Lirio Miranda (202410367)
#
#=======================================================

file_path = "selected_instances/BHW1.dat"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import copy

class Graph:
    def __init__(self):
        with open(file_path, "r") as myFile: # init my graph
            line = myFile.readlines()
            for myLine in line:
                myLine = myLine.strip()

                if myLine.startswith("#Nodes"):
                    separator = myLine.split(":")
                    nodes = int(separator[1].strip())

                elif myLine.startswith("#Edges"):
                    separator = myLine.split(":")
                    edges = int(separator[1].strip())

                elif myLine.startswith("#Arcs"):
                    separator = myLine.split(":")
                    arcs = int(separator[1].strip())

                elif myLine.startswith("#Required N"):
                    separator = myLine.split(":")
                    reN = int(separator[1].strip())
                
                elif myLine.startswith("#Required E"):
                    separator = myLine.split(":")
                    reE = int(separator[1].strip())
                
                elif myLine.startswith("#Required A"):
                    separator = myLine.split(":")
                    reA = int(separator[1].strip())

        self.node = nodes
        self.edges = edges
        self.arc = arcs
        self.reN = reN
        self.reE = reE
        self.reA = reA

        INF = 999
        self.graph = [[INF for i in range(self.node)] for j in range(self.node)]

    def addEdge(self, u, v, cost):
        self.graph[u-1][v-1] = int(cost)
        self.graph[v-1][u-1] = int(cost)

    def addArc(self, u, v, cost):
        self.graph[u-1][v-1] = int(cost)

    def floydWarshall(self):
        d = copy.deepcopy(self.graph) # copy of the graph

        for i in range(self.node):
            for j in range(self.node):
                for k in range(self.node):
                    if(d[i][k] + d[k][j] < d[i][j]):
                        d[i][j] = d[i][k] + d[k][j]
        return d

    def addRoads(self):
        global file_path
        isEdge = False
        isArc = False
        
        with open(file_path, "r") as myFile:
            line = myFile.readlines()
            
            for myLine in line:
                if myLine.startswith(" "):
                    isEdge = False
                    isArc = False

                if isEdge:
                    if myLine.startswith("E"):
                        separator = myLine.split()
                        a = int(separator[1])
                        b = int(separator[2])
                        cost = int(separator[5])
                        self.addEdge(a, b, cost)
                    elif myLine.startswith("NrE"):
                        separator = myLine.split()
                        a = int(separator[1])
                        b = int(separator[2])
                        cost = int(separator[3])
                        self.addEdge(a, b, cost)               
                    
                if isArc:
                    if myLine.startswith("A"):
                        separator = myLine.split()
                        a = int(separator[1])
                        b = int(separator[2])
                        cost = int(separator[5])
                        self.addArc(a, b, cost)
                    elif myLine.startswith("NrA"):
                        separator = myLine.split()
                        a = int(separator[1])
                        b = int(separator[2])
                        cost = int(separator[3])
                        self.addArc(a, b, cost)

                if myLine.startswith(("ReE.", "E")):
                    isEdge = True
                elif myLine.startswith(("EDGE", "NrE")):
                    isEdge = True
                elif myLine.startswith(("ReA.", "A")):
                    isArc = True
                elif myLine.startswith(("ARC", "NrA")):
                    isArc = True
                else:
                    isEdge = False
                    isArc = False

    def density(self):
        dens = (2 * (int(self.edges) + int(self.arc))) / (int(self.node) * (int(self.node) - 1))
        return dens

    def connectedComp(self):
        count = 0
        visited = [False] * self.node

        for start in range(self.node): # bfs
            if visited[start] == False:
                count += 1
                queue = [start]
                visited[start] = True

                while queue:
                    v = queue.pop(0)
                    visited[v] = True

                    for i in range(self.node):
                        if self.graph[v][i] != 999 and visited[i] == False:
                            queue.append(i)
        return count

    def minDegree(self):
        minDeg = 999

        for v in range(self.node):
            degree = 0
            for u in range(self.node):
                if self.graph[v][u] != 999 and v != u: # out
                    degree += 1
                if self.graph[u][v] != 999 and v != u: # in
                    degree += 1
            if degree < minDeg and degree != 0:
                minDeg = degree

        return minDeg

    def maxDegree(self):
        maxDeg = -1

        for v in range(self.node):
            degree = 0
            for u in range(self.node):
                if self.graph[v][u] != 999 and v != u:
                    degree += 1
                if self.graph[u][v] != 999 and v != u:
                    degree += 1
            if degree > maxDeg and degree != 999:
                maxDeg = degree

        return maxDeg

    def maxRoad(self):
        d = self.floydWarshall()
        maxDist = 0
        for i in range(self.node):
            for j in range(self.node):
                if d[i][j] != 999 and d[i][j] > maxDist:
                    maxDist = d[i][j]

        return maxDist

    def averagePathLength(self):
        d = self.floydWarshall()
        total = 0
        checked = False

        for i in range(self.node):
            for j in range(self.node):
                if i != j and d[i][j] != 999:
                    total += d[i][j]
                    checked = True

        if not checked:
            return 0 
        return total / ((self.node) * (self.node - 1))
    
    def betweennessCentrality(self):
        d = self.floydWarshall()
        centrality = [0.0 for _ in range(self.node)]

        for s in range(self.node):
            for t in range(self.node):
                if s != t and d[s][t] != 999:
                    # Para todos os vértices intermediários v
                    for v in range(self.node):
                        if v != s and v != t:
                            # Se v estiver no caminho mínimo entre s e t
                            if d[s][v] + d[v][t] == d[s][t]:
                                centrality[v] += 1

        return centrality

    def showStatistics(self):

        print(f'\n1. Quantidade de vertices: {self.node}')
        print(f'2. Quantidade de arestas: {self.edges}')
        print(f'3. Quantidade de arcos: {self.arc}')
        print(f'4. Quantidade de vertices requeridos: {self.reN}')
        print(f'5. Quantidade de arestas requeridas: {self.reE}')
        print(f'6. Quantidade de arcos requeridos: {self.reA}')
        print(f'7. Densidade do grafo (order strength): {self.density()}')
        print(f'8. Componentes conectados: {self.connectedComp()}')
        print(f'9. Grau minimo dos vertices: {self.minDegree()}')
        print(f'10. Grau maximo dos vertices: {self.maxDegree()}')

        centrality = self.betweennessCentrality()
        print('11. Intermediação:')
        for i, c in enumerate(centrality):
            print(f'    - Nó {i+1}: {c}')

        print(f'12. Caminho medio: {self.averagePathLength()}')
        print(f'13. Diametro: {self.maxRoad()} \n')

    def printGraph(self):
        for i in range(self.node):
            print(self.graph[i])

# ======================= DESENHAR ESTATISTICAS DO GRAFO ==============================
# 
def get_statistics_dataframe(g: Graph):
    stats = {
        "Estatística": [
            "Quantidade de vértices",
            "Quantidade de arestas",
            "Quantidade de arcos",
            "Vértices requeridos",
            "Arestas requeridas",
            "Arcos requeridos",
            "Densidade",
            "Componentes conectados",
            "Grau mínimo",
            "Grau máximo",
            "Caminho médio",
            "Diâmetro"
        ],
        "Valor": [
            g.node,
            g.edges,
            g.arc,
            g.reN,
            g.reE,
            g.reA,
            round(g.density(), 4),
            g.connectedComp(),
            g.minDegree(),
            g.maxDegree(),
            round(g.averagePathLength(), 4),
            g.maxRoad()
        ]
    }

    return pd.DataFrame(stats)

def get_betweenness_dataframe(g: Graph):
    centrality = g.betweennessCentrality()
    data = {
        "Nó": [f"V{i+1}" for i in range(len(centrality))],
        "Intermediação": centrality
    }

    return pd.DataFrame(data)

def ascii_bar_chart(g: Graph, width=40):
    df = get_betweenness_dataframe(g)
    max_val = max(df["Intermediação"])
    for _, row in df.iterrows():
        bar_len = int((row["Intermediação"] / max_val) * width) if max_val > 0 else 0
        bar = '█' * bar_len
        print(f'{row["Nó"]:>4}: {bar} ({row["Intermediação"]})')

def get_adjacency_matrix(g: Graph):
    matriz = np.array(g.graph, dtype=object)
    matriz[matriz == 999] = '∞'

    df = pd.DataFrame(matriz)
    df.columns = [f'V{i+1}' for i in range(g.node)]
    df.index = [f'V{i+1}' for i in range(g.node)]

    return df

def show_betweenness_bars(g):
    df = get_betweenness_dataframe(g)
    return df.style.bar(subset=["Intermediação"], color='#5fba7d')

# Função para gráfico ASCII
def ascii_bar_chart(g, width=40):
    df = get_betweenness_dataframe(g)
    max_val = max(df["Intermediação"])
    for _, row in df.iterrows():
        bar_len = int((row["Intermediação"] / max_val) * width) if max_val > 0 else 0
        bar = '█' * bar_len
        print(f'{row["Nó"]:>4}: {bar} ({row["Intermediação"]})')

def draw_graph(g: Graph, figsize=(8, 6)):
    plt.figure(figsize=figsize)
    positions = {}

    # Gerar posições circulares para os nós
    angle = 2 * np.pi / g.node
    radius = 10
    for i in range(g.node):
        theta = angle * i
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        positions[i] = (x, y)
        plt.text(x, y + 0.5, f'V{i+1}', ha='center', fontsize=9, fontweight='bold')

    # Desenhar arestas e arcos
    for i in range(g.node):
        for j in range(g.node):
            weight = g.graph[i][j]
            if weight != 999:
                x1, y1 = positions[i]
                x2, y2 = positions[j]

                # Desenhar arco (com seta)
                if g.graph[j][i] == 999:  # arco direcionado i -> j
                    plt.arrow(x1, y1, x2 - x1, y2 - y1,
                              length_includes_head=True,
                              head_width=0.4, head_length=0.7,
                              fc='red', ec='red', alpha=0.6)
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2,
                             f'{weight}', fontsize=8, color='red')
                elif i < j:  # aresta não-direcionada
                    plt.plot([x1, x2], [y1, y2], 'b-', alpha=0.5)
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2,
                             f'{weight}', fontsize=8, color='blue')

    plt.axis('off')
    plt.title('Visualização do Grafo')
    plt.show()

# =================================================================================