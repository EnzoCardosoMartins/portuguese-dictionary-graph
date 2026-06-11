import json
import networkx as nx

ARQUIVO_JSONL = "../dados/grafo_arestas.jsonl"
ARQUIVO_EXPORTADO = "../dados/dicionario_completo.gexf"


def exportar_para_gephi():
    # 1. Inicializa o Grafo Direcionado
    G = nx.DiGraph()

    print("[*] Lendo JSONL e montando estrutura na memória...")
    with open(ARQUIVO_JSONL, "r", encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            dados = json.loads(linha)
            origem = dados["origem"]

            G.add_node(origem)
            for destino in dados["destinos"]:
                G.add_edge(origem, destino)

    # 2. Exporta direto para o formato do Gephi
    print(f"[*] Exportando grafo completo para '{ARQUIVO_EXPORTADO}'...")
    nx.write_gexf(G, ARQUIVO_EXPORTADO)
    print("[+] Sucesso! Arquivo pronto para ser aberto no Gephi.")


if __name__ == "__main__":
    exportar_para_gephi()
