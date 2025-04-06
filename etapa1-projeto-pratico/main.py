#=======================================================
#   Authors:
#       . Fábio Damas Valim (202410372)
#       . Guilherme Lirio Miranda (202410367)
#
#=======================================================

file_path = "selected_instances/BHW1.dat"

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

        print(f'11. Intermediacao: ')
        print(f'12. Caminho medio: {self.averagePathLength()}')
        print(f'13. Diametro: {self.maxRoad()} \n')

    def printGraph(self):
        for i in range(self.node):
            print(self.graph[i])