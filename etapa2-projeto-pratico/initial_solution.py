#=======================================================
#   Authors:
#       . Fábio Damas Valim (202410372)
#       . Guilherme Lirio Miranda (202410367)
#
#=======================================================

import os
from main import Graph
import traceback
import time

# Classe responsável por construir uma solução inicial para o problema de roteamento
class initialSolution:
    def __init__(self, graph: Graph, vehicle_capacity: int):
        self.graph = graph
        self.capacity = vehicle_capacity  # Capacidade do veículo
        self.routes = []  # Lista de rotas construídas
        self.total_cost = 0  # Custo total da solução
        self.dist_matrix = self.graph.floydWarshall()  # Matriz de distâncias via Floyd-Warshall
        self.required_nodes = []  # Nós com demanda
        self.required_edges = []  # Arestas com demanda
        self.required_arcs = []  # Arcos com demanda
        self.service_ids = {}  # Mapeia cada serviço para um ID único
        self.depot = 0  # Nó do depósito (fixo como pedido)
        self.day = 1  # Dia fixo para a solução
        self.service_counter = 1  # Contador de serviços para gerar IDs únicos
        self.best_solution_time = 1e24
        self.parse_required_services()  # Carrega serviços obrigatórios do arquivo

    # Lê o arquivo de instância e extrai os serviços obrigatórios
    def parse_required_services(self):
        path = self.graph.file_path
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                section = None
                for line in lines:
                    line = line.strip()
                    # Identifica em qual seção está
                    if line.startswith("ReN."):
                        section = "ReN"
                        continue
                    elif line.startswith("ReE."):
                        section = "ReE"
                        continue
                    elif line.startswith("ReA."):
                        section = "ReA"
                        continue
                    elif line == "" or line.startswith("#") or line.startswith("Name:") or line.startswith("Capacity:"):
                        section = None
                        continue

                    # Parse de nós com demanda
                    if section == "ReN" and line.startswith("N"):
                        parts = line.split()
                        node = int(parts[0][1:]) - 1  # Converte N4 -> 3
                        demand = int(parts[1])
                        self.required_nodes.append((node, demand))
                        self.service_ids[("N", node)] = self.service_counter
                        self.service_counter += 1

                    # Parse de arestas com demanda
                    elif section == "ReE" and line.startswith("E"):
                        parts = line.split()
                        u = int(parts[1]) - 1
                        v = int(parts[2]) - 1
                        demand = int(parts[4])
                        edge = (u, v)
                        self.required_edges.append((edge, demand))
                        self.service_ids[("E", edge)] = self.service_counter
                        self.service_counter += 1

                    # Parse de arcos com demanda
                    elif section == "ReA" and line.startswith("A"):
                        parts = line.split()
                        u = int(parts[1]) - 1
                        v = int(parts[2]) - 1
                        demand = int(parts[4])
                        arc = (u, v)
                        self.required_arcs.append((arc, demand))
                        self.service_ids[("A", arc)] = self.service_counter
                        self.service_counter += 1

        except Exception as e:
            print(f"Erro ao ler serviços do arquivo {path}: {str(e)}")
            raise

    # Constrói rotas viáveis respeitando a capacidade do veículo
    def build_routes(self):
        self.start_time = time.perf_counter()  # início da execução total

        self.best_solution_time = None  # tempo da melhor solução (vai ser definido ao longo do processo)
        self.start_time_best = None     # tempo em que a melhor solução foi encontrada

        # Lista de todos os serviços restantes a serem atendidos
        remaining = list(self.required_nodes + self.required_edges + self.required_arcs)

        while remaining:
            route = []      # Rota atual
            cost = 0        # Custo da rota atual
            demand = 0      # Demanda acumulada
            visits = 1      # Começa com visita ao depósito
            current = self.depot
            
            route.append("(D 0,1,1)")  # Início da rota (no depósito)

            i = 0
            while i < len(remaining):
                item = remaining[i]

                # Serviço em um nó
                if isinstance(item[0], int):
                    node = item[0]
                    if demand + item[1] <= self.capacity:
                        cost += self.dist_matrix[current][node]
                        demand += item[1]
                        sid = self.service_ids[("N", node)]
                        route.append(f"(S {sid},{node+1},{node+1})")
                        current = node
                        remaining.pop(i)
                        visits += 1
                        continue

                # Serviço em uma aresta ou arco
                elif isinstance(item[0], tuple):
                    u, v = item[0]
                    if demand + item[1] <= self.capacity:
                        # Checa se é possível visitar (u,v)
                        if 0 <= u < len(self.graph.graph) and 0 <= v < len(self.graph.graph[u]) and self.graph.graph[u][v] != 999:
                            cost += self.dist_matrix[current][u] + self.graph.graph[u][v]
                            sid = self.service_ids.get(("E", (u, v)), self.service_ids.get(("A", (u, v))))
                            route.append(f"(S {sid},{u+1},{v+1})")
                            demand += item[1]
                            current = v
                            remaining.pop(i)
                            visits += 1
                            continue
                        # Tenta a direção inversa (v,u)
                        elif 0 <= v < len(self.graph.graph) and 0 <= u < len(self.graph.graph[v]) and self.graph.graph[v][u] != 999:
                            cost += self.dist_matrix[current][v] + self.graph.graph[v][u]
                            sid = self.service_ids.get(("E", (v, u)), self.service_ids.get(("A", (v, u))))
                            route.append(f"(S {sid},{v+1},{u+1})")
                            demand += item[1]
                            current = u
                            remaining.pop(i)
                            visits += 1
                            continue
                i += 1

            # Retorno ao depósito
            if current != self.depot:
                cost += self.dist_matrix[current][self.depot]
                route.append("(D 0,1,1)")
                visits += 1

            # Salva a rota construída
            self.routes.append({
                "demand": demand,
                "cost": cost,
                "visits": visits,
                "route": route
            })

            if self.start_time_best is None:
                self.start_time_best = time.perf_counter()

            # Atualiza o custo total
            self.total_cost += cost

        self.end_time = time.perf_counter()    

        # Considera que a solução foi construída neste ponto
        self.best_solution_time = self.end_time - self.start_time_best if self.start_time_best else self.end_time - self.start_time
        self.total_time = self.end_time - self.start_time

    # Gera o arquivo de saída com a solução construída
    def write_solution(self, output_file):
        cpu_freq_hz = 2500000000
        total_clocks = int(self.total_time * cpu_freq_hz)
        best_clocks = int(self.best_solution_time * cpu_freq_hz)

        with open(output_file, "w") as f:
            f.write(f"{int(self.total_cost)}\n")        # Linha 1: Custo total
            f.write(f"{len(self.routes)}\n")            # Linha 2: Total de rotas
            f.write(f"{total_clocks}\n")                # Linha 3: Total de clocks
            f.write(f"{best_clocks}\n")                 # Linha 4: Total de clocks da melhor solucao
            for i, r in enumerate(self.routes):
                # Linha de rota: depósito dia id demanda custo visitas (tripla tripla ...)
                f.write(f" {self.depot} {self.day} {i+1} {r['demand']} {int(r['cost'])} {r['visits']} ")
                for tripla in r["route"]:
                    f.write(f"{tripla} ")
                f.write("\n")

# Função que processa todas as instâncias de um diretório
def process_all_instances(selected_folder="MCGRP", output_folder="G6", vehicle_capacity=30):
    os.makedirs(output_folder, exist_ok=True)
    
    dat_files = [f for f in os.listdir(selected_folder) if f.endswith('.dat')]
    print(f"Encontrados {len(dat_files)} arquivos .dat para processar")
    
    successful = 0
    failed = 0
    
    for filename in dat_files:
        print(f"\nProcessando: {filename}")
        full_path = os.path.join(selected_folder, filename)

        try:
            # Lê capacidade do veículo do próprio arquivo .dat
            with open(full_path, "r") as f:
                for line in f:
                    if line.startswith("Capacity:"):
                        vehicle_capacity = int(line.split(":")[1].strip())
                        break

            print(f"Criando grafo para {filename}...")
            g = Graph(full_path)
            g.addRoads()

            print(f"Construindo solução para {filename}...")
            solver = initialSolution(g, vehicle_capacity)
            solver.build_routes()

            output_name = f"sol-{filename}"
            output_path = os.path.join(output_folder, output_name)
            print(f"Escrevendo solução em {output_path}...")
            solver.write_solution(output_path)
            print(f"Solução gerada com sucesso para {filename}")
            successful += 1
            
        except Exception as e:
            print(f"Erro ao processar {filename}:")
            print(f"Tipo do erro: {type(e).__name__}")
            print(f"Mensagem do erro: {str(e)}")
            traceback.print_exc()
            failed += 1
            continue  # Continua com o próximo arquivo
    
    print("\nResumo do processamento:")
    print(f"Total de arquivos processados: {len(dat_files)}")
    print(f"Arquivos processados com sucesso: {successful}")
    print(f"Arquivos com erro: {failed}")

if __name__ == "__main__":
    process_all_instances()