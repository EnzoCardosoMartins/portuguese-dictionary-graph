import json
import networkx as nx

ARQUIVO_JSONL = "../dados/grafo_arestas.jsonl"

def carregar_e_analisar_grafo():
    # 1. Inicializa um Grafo Direcionado (as conexões importam o sentido: Origem -> Destino)
    G = nx.DiGraph()
    
    print("Carregando as arestas do arquivo JSONL...")
    
    with open(ARQUIVO_JSONL, "r", encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            
            dados = json.loads(linha)
            origem = dados["origem"]
            destinos = dados["destinos"]
            
            # Adiciona o vértice de origem (a palavra que está sendo definida)
            G.add_node(origem)
            
            # Adiciona as arestas para cada palavra da definição
            for destino in destinos:
                G.add_edge(origem, destino)
                
    print("\n=== ESTRUTURA DO GRAFO GERADA ===")
    print(f"Total de Vértices (Palavras Únicas): {G.number_of_nodes():,}")
    print(f"Total de Arestas (Conexões Semânticas): {G.number_of_edges():,}")
    print("==================================\n")
    
    return G


def analise_hubs_por_in_degree(grafo_dicionario):
    # 2. Descobrir os maiores Hubs (Palavras com maior In-Degree)
    print("Calculando as palavras mais fundamentais (maior In-Degree)...")
    graus_entrada = dict(grafo_dicionario.in_degree())

    # Ordena do maior para o menor e pega o top 15
    top_hubs = sorted(graus_entrada.items(), key=lambda x: x[1], reverse=True)[:15]

    print("\n--- TOP 15 CONCEITOS FUNDAMENTAIS ---")
    for palavra, grau in top_hubs:
        print(f"{palavra}: usado em {grau:,} definições")


def componentes_fortemente_conectados(grafo_dicionario):
    # 3. Encontrar Componentes Fortemente Conectados (SCC)
    print("\nAnalisando loops lógicos (Componentes Fortemente Conectados)...")
    scc = list(nx.strongly_connected_components(grafo_dicionario))

    # Ordena os componentes pelo tamanho
    scc_ordenados = sorted(scc, key=len, reverse=True)

    print(f"Total de loops fechados encontrados: {len(scc_ordenados):,}")
    print(f"Tamanho do maior loop circular da língua: {len(scc_ordenados[0])} palavras.")


'''
def caminho_conceitual(grafo, inicio, fim):
    try:
        caminho = nx.shortest_path(grafo, source=inicio, target=fim)
        print(f"\nCaminho de '{inicio}' até '{fim}':")
        print(" -> ".join(caminho))
    except nx.NetworkXNoPath:
        print(f"\nNão existe nenhum caminho que conecte '{inicio}' a '{fim}'.")
    except nx.NodeNotFound as e:
        print(f"\nErro: {e}")

# Exemplo de teste (mude para palavras que você sabe que existem no seu dataset)
caminho_conceitual(grafo_dicionario, "abelha", "filosofia")
'''


if __name__ == "__main__":
    grafo_dicionario = carregar_e_analisar_grafo()
    analise_hubs_por_in_degree(grafo_dicionario)
    componentes_fortemente_conectados(grafo_dicionario)

    
