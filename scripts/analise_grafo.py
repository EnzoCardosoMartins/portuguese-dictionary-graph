import argparse
import json
import sys
import networkx as nx

ARQUIVO_JSONL = "../dados/grafo_arestas.jsonl"
ARQUIVO_TXT_SAIDA = "../dados/ranking_completo_conexoes.txt"


# ==========================================
# 1. FUNÇÃO BÁSICA (Roda sempre)
# ==========================================
def carregar_grafo(caminho_jsonl):
    """Lê o arquivo JSONL e monta o Grafo Direcionado na memória."""
    G = nx.DiGraph()
    print(f"[*] Carregando as arestas de '{caminho_jsonl}'...")

    try:
        with open(caminho_jsonl, "r", encoding="utf-8") as f:
            for linha in f:
                if not linha.strip():
                    continue
                dados = json.loads(linha)
                origem = dados["origem"]
                G.add_node(origem)
                for destino in dados["destinos"]:
                    G.add_edge(origem, destino)
    except FileNotFoundError:
        print(f"[Erro] Arquivo '{caminho_jsonl}' não encontrado. Gere o JSONL primeiro.")
        sys.exit(1)

    print("\n=== ESTRUTURA DO GRAFO GERADA ===")
    print(f"Total de Vértices (Palavras Únicas): {G.number_of_nodes():,}")
    print(f"Total de Arestas (Conexões Semânticas): {G.number_of_edges():,}")
    print("==================================\n")
    return G


# ==========================================
# 2. FUNÇÕES DE ANÁLISE (Ativadas por flags)
# ==========================================
def analisar_top_hubs(G, top_n=15):
    """Calcula o grau de entrada (In-Degree) e exibe o Top N no terminal."""
    print(f"[*] Calculando o grau de conectividade das palavras...")
    graus_entrada = dict(G.in_degree())

    ranking_completo = sorted(
        graus_entrada.items(), key=lambda x: x[1], reverse=True
    )

    print(f"\n--- TOP {top_n} CONCEITOS FUNDAMENTAIS (IN-DEGREE) ---")
    for i, (palavra, in_degree) in enumerate(ranking_completo[:top_n], 1):
        out_degree = G.out_degree(palavra)
        print(
            f"{i:02d}. {palavra:<15} -> Usado em {in_degree:,} definições | Sua definição usa {out_degree} palavras."
        )
    return ranking_completo


def exportar_ranking_txt(ranking, G, caminho_txt):
    """Salva a lista completa de palavras e suas métricas em um arquivo .txt."""
    print(f"[*] Exportando a lista completa para '{caminho_txt}'...")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write("=== RANKING COMPLETO DE CONECTIVIDADE DO DICIONÁRIO ===\n")
        f.write(f"Formato: Posição. Palavra [In-Degree: X | Out-Degree: Y]\n")
        f.write("-" * 55 + "\n\n")

        for i, (palavra, in_degree) in enumerate(ranking, 1):
            out_degree = G.out_degree(palavra)
            f.write(
                f"{i:06d}. {palavra:<25} [In-Degree: {in_degree:<5} | Out-Degree: {out_degree:<4}]\n"
            )
    print("[+] Exportação concluída com sucesso!")


def analisar_ciclos(G):
    """Encontra e analisa os Componentes Fortemente Conectados (SCC)."""
    print("[*] Analisando loops lógicos (Componentes Fortemente Conectados)...")
    scc = list(nx.strongly_connected_components(G))
    scc_ordenados = sorted(scc, key=len, reverse=True)

    print("\n--- ANÁLISE DE CIRCULARIDADE ---")
    print(f"Total de loops fechados (SCCs) encontrados: {len(scc_ordenados):,}")
    if scc_ordenados:
        print(
            f"Tamanho do maior loop circular da língua: {len(scc_ordenados[0])} palavras."
        )


def buscar_caminho_minimo(G, inicio, fim):
    """Busca a menor cadeia de definições que conecta duas palavras."""
    print(f"[*] Buscando o menor caminho conceitual de '{inicio}' até '{fim}'...")
    try:
        caminho = nx.shortest_path(G, source=inicio, target=fim)
        print("\n--- CAMINHO MÍNIMO CONCEITUAL ---")
        print(" -> ".join(caminho))
    except nx.NetworkXNoPath:
        print(
            f"\n[-] Não existe nenhum caminho direcionado que conecte '{inicio}' a '{fim}'."
        )
    except nx.NodeNotFound as e:
        print(f"\n[Erro] {e} (Verifique se digitou a palavra corretamente)")


# ==========================================
# 3. CONTROLE DE FLUXO E ARGS
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Engine de Análise do Grafo do Dicionário Semântico."
    )

    # Definição das flags
    parser.add_argument(
        "--all",
        action="store_true",
        help="Executa todas as análises disponíveis de uma vez só",
    )
    parser.add_argument(
        "--ranking",
        action="store_true",
        help="Exibe o Top 15 e exporta o ranking completo para .txt",
    )
    parser.add_argument(
        "--ciclos",
        action="store_true",
        help="Analisa a circularidade e os Componentes Fortemente Conectados",
    )
    parser.add_argument(
        "--caminho",
        nargs=2,
        metavar=("PALAVRA1", "PALAVRA2"),
        help="Encontra o menor caminho conceitual entre duas palavras (Ex: --caminho abelha filosofia)",
    )

    args = parser.parse_args()

    # Se o usuário executar sem nenhuma flag, exibe o aviso de carregamento básico
    if not (args.all or args.ranking or args.ciclos or args.caminho):
        print("[!] Nenhuma flag de análise informada. Rodando apenas o carregamento básico.\n")

    # 1. Roda sempre (Função básica)
    G = carregar_grafo(ARQUIVO_JSONL)

    # 2. Execuções condicionais baseadas nas flags do terminal
    if args.all or args.ranking:
        ranking = analisar_top_hubs(G, top_n=15)
        exportar_ranking_txt(ranking, G, ARQUIVO_TXT_SAIDA)

    if args.all or args.ciclos:
        analisar_ciclos(G)

    if args.caminho:
        buscar_caminho_minimo(G, args.caminho[0].lower(), args.caminho[1].lower())
    elif args.all:
        # Caminho padrão executado quando o --all é chamado sem parâmetros de caminho extras
        buscar_caminho_minimo(G, "abelha", "ciência")


if __name__ == "__main__":
    main()
