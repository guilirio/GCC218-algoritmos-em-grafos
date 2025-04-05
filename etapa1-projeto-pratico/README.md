# Etapa 1: Pré-processamento dos dados

```
EQUIPE:
   . Fábio Damas Valim (202410372)
   . Guilherme Lirio Miranda (202410367)

```

Os objetivos da Etapa 1 consistem em:
- representar a modelagem do problema por meio de estruturas de dados
em grafos;
- implementação da leitura dos dados;
- cálculo de estatísticas a respeito dos grafos.

## Estrutura do Projeto

- `main.py`: Responsável pela leitura, modelagem e cálculos estatísticos do grafo.
- `my_statistics.ipynb`: Executa a visualização do algoritmo.
- `selected_instances/BHW1.dat`: Arquivo de entrada com a descrição do grafo.
- `README.md`: Documentação do projeto.

---

## Lógica e Implementações

### Leitura do Arquivo

```python
with open(file_path, "r") as myFile:
    line = myFile.readlines()
    for myLine in line:
        myLine = myLine.strip()
        if myLine.startswith("#Nodes"):
            ...
```
A leitura começa identificando o número de nós, arestas, arcos e elementos requeridos através das palavras-chave no arquivo `.dat.`

### Inicialização da Matriz de Adjacência

```python
INF = 999
self.graph = [[INF for i in range(self.node)] for j in range(self.node)]
```
Utiliza-se uma matriz de adjacência para representar o grafo. O valor 999 representa a ausência de ligação entre os vértices.

### Adição de Arestas e Arcos

```python
# Adicao de arestas
def addEdge(self, u, v, cost):
    self.graph[u-1][v-1] = int(cost)
    self.graph[v-1][u-1] = int(cost)
```
```python
# Adicao de arcos
def addArc(self, u, v, cost):
    self.graph[u-1][v-1] = int(cost)
```
As arestas são adicionadas como conexões bidirecionais, e os arcos como direcionais.

### Floyd-Warshall

```python
def floydWarshall(self):
    d = copy.deepcopy(self.graph)
    for i in range(self.node):
        for j in range(self.node):
            for k in range(self.node):
                if(d[i][k] + d[k][j] < d[i][j]):
                    d[i][j] = d[i][k] + d[k][j]
    return d
```
Algoritmo utilizado para calcular o caminho mínimo entre todos os pares de vértices, essencial para determinar o diâmetro do grafo.

### Cálculo da Densidade

```python
def density(self):
    dens = (2 * (self.edges + self.arc)) / (self.node * (self.node - 1))
    return dens
```
Densidade de um multigrafo: considera o total de conexões (arestas + arcos) sobre o número máximo possível de conexões.

### Grau Mínimo

```python
def minDegree(self):
    minDeg = 999
    for v in range(self.node):
        degree = 0
        for u in range(self.node):
            if self.graph[v][u] != 999 and v != u:
                degree += 1
            if self.graph[u][v] != 999 and v != u:
                degree += 1
        if degree < minDeg and degree != 0:
            minDeg = degree
    return minDeg
```
Calcula o menor grau entre todos os vértices (entrada + saída), ignorando vértices isolados percorrendo a matriz.

### Grau Máximo

```python
def maxDegree(self):
    maxDeg = -1
    for v in range(self.node):
        degree = 0
        for u in range(self.node):
            if self.graph[v][u] != 999 and v != u:
                degree += 1
            if self.graph[u][v] != 999 and v != u:
                degree += 1
        if degree > maxDeg:
            maxDeg = degree
    return maxDeg
```
Calcula o maior grau entre todos os vértices (entrada + saída).

### Componentes Conectados

```python
def connectedComp(self):
    count = 0
    visited = [False] * self.node
    for start in range(self.node):
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
```
Utilizamos o algoritmo de Busca em largura (BFS) para identificar quantos componentes conectadas existem no grafo.

### Diâmetro (Maior Caminho Mínimo)

```python
def maxRoad(self):
    d = self.floydWarshall()
    maxDist = 0
    for i in range(self.node):
        for j in range(self.node):
            if d[i][j] != 999 and d[i][j] > maxDist:
                maxDist = d[i][j]
    return maxDist
```
Determina o maior valor entre os menores caminhos entre todos os pares de vértices: isso define o diâmetro do grafo.

### Visualização

A visualização é feita no arquivo `my_statistics.ipynb` com as seguintes etapas:

```python
import importlib
import main

importlib.reload(main)

graph = main.Graph()
graph.addRoads()
graph.showStatistics()
```
o módulo `importlib` regarrega/atualiza a main sem precisar reiniciar tudo.
Exibe todas as estatísticas no console de forma organizada.

---

### Exemplo de Saída

```markdown
1. Quantidade de vertices: 12
2. Quantidade de arestas: 11
3. Quantidade de arcos: 22
4. Quantidade de vertices requeridos: 7
5. Quantidade de arestas requeridas: 11
6. Quantidade de arcos requeridos: 11
7. Densidade do grafo (order strength): 0.5
8. Componentes conectados: 2
9. Grau minimo dos vertices: 2
10. Grau maximo dos vertices: 6
11. Intermediacao:
12. Caminho medio: 
13. Diametro: 65 
```