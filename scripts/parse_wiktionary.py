from pathlib import Path
import xml.etree.ElementTree as ET
import json
import spacy
from tqdm import tqdm

# Inicializa o spaCy
nlp = spacy.load("pt_core_news_lg")

# Define os caminhos
DIRETORIO_XMLS = Path("../dados/xmls")
ARQUIVO_SAIDA = "../dados/grafo_arestas.jsonl"

def processar_arquivo_xml(caminho_xml, f_out):
    """Processa um único arquivo XML e escreve os resultados no arquivo de saída."""
    try:
        # Usa o iterparse para carregar a árvore de tags sob demanda
        context = ET.iterparse(caminho_xml, events=("end",))
        
        for event, elem in context:
            if elem.tag == "entry":
                orth_el = elem.find(".//orth")
                def_el = elem.find(".//def")
                
                if orth_el is not None and def_el is not None and orth_el.text and def_el.text:
                    palavra_origem = orth_el.text.strip().lower()
                    texto_definicao = def_el.text.strip()
                    
                    # Passa o spaCy na definição da palavra
                    doc = nlp(texto_definicao)
                    vertices_destino = []
                    
                    for token in doc:
                        if not token.is_stop and not token.is_punct and token.is_alpha:
                            vertices_destino.append(token.lemma_.lower())
                    
                    # Elimina duplicatas de conexões dentro da mesma definição
                    vertices_destino = list(set(vertices_destino))
                    
                    if vertices_destino:
                        registro = {
                            "origem": palavra_origem,
                            "destinos": vertices_destino
                        }
                        f_out.write(json.dumps(registro, ensure_ascii=False) + "\n")
                
                # Libera o elemento da memória RAM
                elem.clear()
                
    except ET.ParseError as e:
        print(f"\n[Erro] Falha ao parsear o arquivo {caminho_xml.name}: {e}")
    except Exception as e:
        print(f"\n[Erro] Erro inesperado no arquivo {caminho_xml.name}: {e}")

def pipeline_principal():
    # Encontra todos os arquivos .xml dentro da pasta informada
    arquivos_xml = list(DIRETORIO_XMLS.glob("*.xml"))
    
    if not arquivos_xml:
        print(f"Nenhum arquivo .xml encontrado na pasta '{DIRETORIO_XMLS}'. Verifique o caminho.")
        return

    print(f"Encontrados {len(arquivos_xml)} arquivos para processamento.")
    
    # Abre o arquivo de saída único em modo 'w' (write)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f_out:
        # Tqdm cria uma barra de progresso estilosa no terminal por arquivo
        for caminho_xml in tqdm(arquivos_xml, desc="Processando Alfabeto"):
            processar_arquivo_xml(caminho_xml, f_out)

if __name__ == "__main__":
    pipeline_principal()
    print(f"\nSucesso! O pipeline unificou todos os arquivos em '{ARQUIVO_SAIDA}'.")
