#=======================================================
#   Authors:
#       . Fábio Damas Valim (202410372)
#       . Guilherme Lirio Miranda (202410367)
#
#=======================================================

import os
from main import Graph
import time
import concurrent.futures

# Classe responsável por construir uma solução inicial para o problema de roteamento
# Essa solução agrupa serviços com demanda em rotas viáveis, respeitando a capacidade do veículo
class InitialSolution:
    def __init__(self, graph: Graph, vehicle_capacity: int):
        # Armazena o grafo de entrada
        self.graph = graph

        # Capacidade máxima do veículo
        self.capacity = vehicle_capacity

        # Lista de rotas construídas na solução
        self.routes = []

        # Custo total acumulado das rotas
        self.total_cost = 0

        # Matriz de distâncias entre todos os pares de vértices, calculada com Floyd-Warshall
        self.dist_matrix = self.graph.floydWarshall()

        # Listas que armazenam os serviços obrigatórios: em nós, arestas e arcos
        self.required_nodes = []
        self.required_edges = []
        self.required_arcs = []

        # Dicionário que associa um ID único para cada serviço (nó, aresta ou arco)
        self.service_ids = {}

        # Nó de partida/chegada das rotas (depósito), fixado como 0
        self.depot = 0

        # Dia fixo para a construção das rotas (pode ser relevante para compatibilidade com formatos de saída)
        self.day = 1

        # Contador usado para gerar IDs únicos para os serviços
        self.service_counter = 1

        # Armazena o tempo em que a melhor solução foi encontrada
        self.best_solution_time = None

        # Carrega os serviços obrigatórios a partir do arquivo de instância
        self.parse_required_services()

    # Lê o arquivo de entrada da instância para identificar os serviços obrigatórios
    def parse_required_services(self):
        path = self.graph.file_path
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                section = None
                for line in lines:
                    line = line.strip()

                    # Identifica início de uma seção de serviços
                    if line.startswith("ReN."):
                        section = "ReN"  # Serviços em nós
                        continue
                    elif line.startswith("ReE."):
                        section = "ReE"  # Serviços em arestas
                        continue
                    elif line.startswith("ReA."):
                        section = "ReA"  # Serviços em arcos
                        continue
                    elif line == "" or line.startswith("#") or line.startswith("Name:") or line.startswith("Capacity:"):
                        section = None  # Ignora outras linhas
                        continue

                    # Lê serviços em nós
                    if section == "ReN" and line.startswith("N"):
                        parts = line.split()
                        node = int(parts[0][1:]) - 1  # N4 -> índice 3
                        demand = int(parts[1])
                        self.required_nodes.append((node, demand))
                        self.service_ids[("N", node)] = self.service_counter
                        self.service_counter += 1

                    # Lê serviços em arestas
                    elif section == "ReE" and line.startswith("E"):
                        parts = line.split()
                        u = int(parts[1]) - 1
                        v = int(parts[2]) - 1
                        demand = int(parts[4])
                        edge = (u, v)
                        self.required_edges.append((edge, demand))
                        self.service_ids[("E", edge)] = self.service_counter
                        self.service_counter += 1

                    # Lê serviços em arcos
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

    # Constrói rotas a partir dos serviços obrigatórios, respeitando a capacidade do veículo
    def build_routes(self):
        self.start_time = time.perf_counter()  # Marca o início do tempo total de execução
        self.best_solution_time = None
        self.start_time_best = None

        # Unifica todos os serviços obrigatórios em uma lista
        all_services = list(self.required_nodes + self.required_edges + self.required_arcs)

        # Ordena os serviços por distância do depósito (prioriza os mais próximos)
        def service_distance(service):
            if isinstance(service[0], int):  # Nó
                node = service[0]
                return self.dist_matrix[self.depot][node]
            elif isinstance(service[0], tuple):  # Aresta ou arco
                u, v = service[0]
                return min(self.dist_matrix[self.depot][u], self.dist_matrix[self.depot][v])
            return float('inf')

        all_services.sort(key=service_distance)
        remaining = all_services  # Lista de serviços a serem alocados

        # Enquanto ainda houver serviços para alocar
        while remaining:
            route = []          # Inicializa rota atual
            cost = 0            # Custo acumulado da rota
            demand = 0          # Demanda acumulada
            visits = 1          # Número de visitas na rota
            current = self.depot
            route.append(f"(D 0,{self.day},{self.day})")  # Início da rota

            while True:
                # Filtra serviços que cabem na capacidade restante
                candidates = [item for item in remaining if demand + item[1] <= self.capacity]
                if not candidates:
                    break

                # Escolhe o mais próximo do ponto atual
                def dist_from_current(service):
                    if isinstance(service[0], int):
                        return self.dist_matrix[current][service[0]]
                    elif isinstance(service[0], tuple):
                        u, v = service[0]
                        return min(self.dist_matrix[current][u], self.dist_matrix[current][v])
                    return float('inf')

                next_service = min(candidates, key=dist_from_current)
                remaining.remove(next_service)

                # Adiciona serviço à rota
                if isinstance(next_service[0], int):  # Nó
                    node = next_service[0]
                    cost += self.dist_matrix[current][node]
                    demand += next_service[1]
                    sid = self.service_ids[("N", node)]
                    route.append(f"(S {sid},{node+1},{node+1})")
                    current = node
                    visits += 1
                elif isinstance(next_service[0], tuple):  # Aresta ou arco
                    u, v = next_service[0]
                    # Escolhe sentido de menor custo
                    if self.dist_matrix[current][u] + self.graph.graph[u][v] <= self.dist_matrix[current][v] + self.graph.graph[v][u]:
                        cost += self.dist_matrix[current][u] + self.graph.graph[u][v]
                        sid = self.service_ids.get(("E", (u, v)), self.service_ids.get(("A", (u, v))))
                        route.append(f"(S {sid},{u+1},{v+1})")
                        current = v
                    else:
                        cost += self.dist_matrix[current][v] + self.graph.graph[v][u]
                        sid = self.service_ids.get(("E", (v, u)), self.service_ids.get(("A", (v, u))))
                        route.append(f"(S {sid},{v+1},{u+1})")
                        current = u
                    demand += next_service[1]
                    visits += 1

            # Retorna ao depósito
            if current != self.depot:
                cost += self.dist_matrix[current][self.depot]
                route.append("(D 0,1,1)")
                visits += 1

            # Adiciona a rota construída
            self.routes.append({
                "demand": demand,
                "cost": cost,
                "visits": visits,
                "route": route
            })

            # Marca tempo da melhor solução (a primeira encontrada)
            if self.start_time_best is None:
                self.start_time_best = time.perf_counter()

            self.total_cost += cost

        self.end_time = time.perf_counter()

        # Calcula tempo da melhor solução e total
        self.best_solution_time = self.end_time - self.start_time_best if self.start_time_best else self.end_time - self.start_time
        self.total_time = self.end_time - self.start_time

    # Escreve o resultado da solução no arquivo de saída especificado
    def write_solution(self, output_file):
        # Estimativa de clocks de CPU com base em frequência fixa (2.5 GHz)
        cpu_freq_hz = 2500000000
        total_clocks = int(self.total_time * cpu_freq_hz)
        best_clocks = int(self.best_solution_time * cpu_freq_hz)

        with open(output_file, "w") as f:
            f.write(f"{int(self.total_cost)}\n")        # Linha 1: custo total da solução
            f.write(f"{len(self.routes)}\n")            # Linha 2: número de rotas
            f.write(f"{total_clocks}\n")                # Linha 3: clocks totais
            f.write(f"{best_clocks}\n")                 # Linha 4: clocks da melhor solução
            for i, r in enumerate(self.routes):
                # Linha 5+: informações detalhadas de cada rota
                f.write(f" {self.depot} {self.day} {i+1} {r['demand']} {int(r['cost'])} {r['visits']} ")
                for tripla in r["route"]:
                    f.write(f"{tripla} ")
                f.write("\n")

# Função auxiliar que processa uma única instância (arquivo .dat) e gera sua solução
def process_instance(args):
    filename, selected_folder, output_folder = args
    full_path = os.path.join(selected_folder, filename)
    try:
        # Extrai a capacidade do veículo a partir do arquivo
        with open(full_path, "r") as f:
            for line in f:
                if line.startswith("Capacity:"):
                    vehicle_capacity = int(line.split(":")[1].strip())
                    break

        # Cria o grafo e carrega as estradas
        g = Graph(full_path)
        g.addRoads()

        # Constrói a solução inicial
        solver = InitialSolution(g, vehicle_capacity)
        solver.build_routes()

        # Gera e salva a saída
        output_name = f"sol-{filename}"
        output_path = os.path.join(output_folder, output_name)
        solver.write_solution(output_path)

        return True, filename
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        return False, filename

# Função principal que processa todas as instâncias (arquivos .dat) em paralelo
def process_all_instances(selected_folder="MCGRP", output_folder="G6"):
    import time
    os.makedirs(output_folder, exist_ok=True)
    dat_files = [f for f in os.listdir(selected_folder) if f.endswith('.dat')]
    print(f"Encontrados {len(dat_files)} arquivos .dat para processar")

    tempo_inicio = time.perf_counter()

    # Cria lista de argumentos (nome de arquivos)
    args_list = [(filename, selected_folder, output_folder) for filename in dat_files]

    successful = 0
    failed = 0

    # Utiliza paralelismo com ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(process_instance, args_list)
        for success, filename in results:
            if success:
                print(f"Solução gerada com sucesso para {filename}")
                successful += 1
            else:
                failed += 1

    tempo_fim = time.perf_counter()
    tempo_total = tempo_fim - tempo_inicio

    # Exibe resumo final
    print("\nResumo do processamento:")
    print(f"Total de arquivos processados: {len(dat_files)}")
    print(f"Arquivos processados com sucesso: {successful}")
    print(f"Arquivos com erro: {failed}")
    print(f"Tempo total de processamento: {tempo_total:.2f} segundos")

# Se o script for executado diretamente, processa todas as instâncias
if __name__ == "__main__":
    process_all_instances()
