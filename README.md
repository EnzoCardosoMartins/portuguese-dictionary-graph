# Portuguese Dictionary Graph

> Transformando o dicionário da língua portuguesa em um grafo semântico dirigido, onde cada palavra é um vértice e cada definição gera arestas para os conceitos que a compõem.

---

## Sobre o Projeto

Este projeto constrói um **grafo semântico da língua portuguesa** a partir do [Dicionário Aberto](https://github.com/próprio-link) — uma obra lexicográfica baseada no dicionário de Cândido de Figueiredo, mantida por Alberto Simões e pela Universidade do Minho. Cada verbete se torna um nó, e cada palavra relevante presente em sua definição gera uma aresta direcionada — revelando quais conceitos são mais fundamentais para a língua, quais palavras formam ciclos de definição circular, e qual o caminho conceitual mínimo entre duas palavras quaisquer.

### Motivação

Dicionários são, por natureza, estruturas de grafo: palavras são definidas em termos de outras palavras. Tornar essa estrutura explícita permite perguntas como:

- Quais são os conceitos mais primitivos da língua — aqueles que aparecem na definição de tudo?
- Existem "ilhas" de palavras que só se definem entre si?
- Quantas etapas conceituais separam *"abelha"* de *"filosofia"*?

---

## Arquitetura do Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FONTE DE DADOS                              │
│                       Dicionário Aberto                             │
│         dados/xmls/  →  A.xml · B.xml · ... · Z.xml                 │
│                         Names.xml · Geo.xml · ...                   │
│      (XML puro · fragmentado por letra · sem compressão)            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    parse_wiktionary.py                              │
│                                                                     │
│  • Varre todos os arquivos .xml do diretório dados/xmls/            │
│  • Lê cada arquivo em streaming (iterparse) — sem carregar na RAM   │
│  • Extrai pares <orth> (palavra) e <def> (definição) de cada entry  │
│  • Tokeniza a definição com spaCy pt_core_news_lg                   │
│  • Remove stopwords e pontuação; aplica lematização                 │
│  • Elimina duplicatas de conexões dentro da mesma definição         │
│                                                                     │
│  SAÍDA → grafo_arestas.jsonl                                        │
│          {"origem": "abelha", "destinos": ["inseto", "mel", ...]}   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      analise_grafo.py                               │
│                                                                     │
│  • Carrega o JSONL e constrói um DiGraph (NetworkX)                 │
│  • CLI dinâmica via argparse — análises ativadas por flags          │
│  • Calcula In-Degree e Out-Degree de todos os nós                   │
│  • Identifica os hubs semânticos (conceitos mais fundamentais)      │
│  • Detecta Componentes Fortemente Conectados (SCCs)                 │
│  • Calcula caminhos mínimos entre pares de palavras                 │
│  • Exporta ranking completo em .txt                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Estrutura do Repositório

```
portuguese-dictionary-graph/
│
├── dados/
│   ├── xmls/                          # Arquivos XML do Dicionário Aberto
│   │   ├── A.xml                      #   Verbetes iniciados por A
│   │   ├── B.xml                      #   Verbetes iniciados por B
│   │   ├── ...                        #   (um arquivo por letra)
│   │   ├── Names.xml                  #   Nomes próprios
│   │   └── Geo.xml                    #   Termos geográficos
│   ├── grafo_arestas.jsonl            # Saída do parser (gerado pelo pipeline)
│   └── ranking_completo_conexoes.txt  # Ranking exportado pela análise
│
├── scripts/
│   ├── parse_wiktionary.py            # Etapa 1: extração e tokenização
│   ├── analise_grafo.py               # Etapa 2: análise do grafo
│   └── requirements.txt
│
└── README.md
```

---

## Instalação

### Pré-requisitos

- Python 3.9+
- ~2 GB de espaço em disco (dump + grafo gerado)
- ~4 GB de RAM para carregar o grafo completo em memória

### 1. Clone o repositório

```bash
git clone https://github.com/EnzoCardosoMartins/portuguese-dictionary-graph
cd portuguese-dictionary-graph
```

### 2. Crie um ambiente virtual e instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

### 3. Obtenha os arquivos do Dicionário Aberto

O dataset é distribuído pelo projeto [Dicionário Aberto](https://github.com/apertium/dicionario-aberto) (obra baseada em Cândido de Figueiredo, mantida por Alberto Simões / Universidade do Minho) e vem estruturado em XML puro, fragmentado por letra.

```bash
mkdir -p dados/xmls
# Clone o repositório do dataset ou copie os XMLs para dados/xmls/
# O diretório deve conter: A.xml, B.xml, ..., Z.xml, Names.xml, Geo.xml, etc.
```

> Diferentemente de dumps comprimidos, os arquivos são XML puro e podem ser inspecionados diretamente em qualquer editor de texto.

---

## Como Usar

### Etapa 1 — Gerar o grafo de arestas

```bash
python parse_wiktionary.py
```

Este script varre todos os arquivos `.xml` dentro de `dados/xmls/`, processa cada verbete e consolida tudo em um único arquivo `dados/grafo_arestas.jsonl`. O progresso é exibido por arquivo (barra de progresso por letra do alfabeto).

**Formato de saída:**
```json
{"origem": "correção", "destinos": ["ato", "efeito", "corrigir", "castigo", "ensinar"]}
{"origem": "divisão", "destinos": ["ato", "dividir", "operação", "inverso", "multiplicação"]}
```

---

### Etapa 2 — Analisar o grafo

O script de análise é controlado por flags de linha de comando:

#### Carregamento básico (estrutura do grafo)

```bash
python analise_grafo.py
```

```
=== ESTRUTURA DO GRAFO GERADA ===
Total de Vértices (Palavras Únicas): 87,432
Total de Arestas (Conexões Semânticas): 1,204,871
==================================
```

#### Top 15 conceitos mais fundamentais + exportação do ranking completo

```bash
python analise_grafo.py --ranking
```

```
--- TOP 15 CONCEITOS FUNDAMENTAIS (IN-DEGREE) ---
01. ser            -> Usado em 12,847 definições | Sua definição usa 8 palavras.
02. relativo       -> Usado em 9,312 definições  | Sua definição usa 5 palavras.
03. qualidade      -> Usado em 8,901 definições  | Sua definição usa 6 palavras.
...
```

O ranking completo é salvo em `dados/ranking_completo_conexoes.txt`.

#### Análise de circularidade (Componentes Fortemente Conectados)

```bash
python analise_grafo.py --ciclos
```

```
--- ANÁLISE DE CIRCULARIDADE ---
Total de loops fechados (SCCs) encontrados: 3,241
Tamanho do maior loop circular da língua: 18,493 palavras.
```

#### Caminho mínimo conceitual entre duas palavras

```bash
python analise_grafo.py --caminho abelha filosofia
```

```
--- CAMINHO MÍNIMO CONCEITUAL ---
abelha -> inseto -> animal -> ser -> existir -> conhecimento -> filosofia
```

#### Executar todas as análises de uma vez

```bash
python analise_grafo.py --all
```

---

## Métricas do Grafo

| Métrica | Descrição |
|---|---|
| **Vértices** | Palavras únicas presentes no vocabulário ou em definições |
| **Arestas** | Conexões dirigidas `palavra → conceito_da_definição` |
| **In-Degree** | Quantas definições usam aquela palavra — mede a *fundamentalidade* |
| **Out-Degree** | Quantas palavras a definição daquela palavra usa — mede a *complexidade* |
| **SCC** | Componente Fortemente Conectado — grupo de palavras mutuamente alcançáveis |
| **Caminho mínimo** | Menor cadeia de definições que conecta dois conceitos |

### Interpretação dos resultados

- **Alto In-Degree + baixo Out-Degree** → palavra primitiva da língua (ex: *ser*, *fazer*, *coisa*)
- **Alto Out-Degree** → definição complexa, que depende de muitos outros conceitos
- **SCC grande** → circularidade extensa — palavras que se definem mutuamente
- **Caminho mínimo longo** → conceitos semanticamente distantes

---

## Decisões Técnicas

### Por que grafo dirigido (`DiGraph`)?

A direção importa semanticamente: a aresta `abelha → inseto` significa *"abelha é definida usando inseto"*, não o contrário. Um grafo não-dirigido perderia essa assimetria fundamental — que é exatamente o que permite calcular quais conceitos são mais *primitivos* (alto In-Degree sem depender de muitos outros).

### Por que lematização?

O spaCy reduz formas flexionadas ao lema base: *"correu"*, *"corre"*, *"correndo"* → *"correr"*. Isso evita que variações morfológicas criem vértices separados para o mesmo conceito, reduzindo o grafo em ~30% e melhorando a qualidade semântica.

### Por que remover stopwords?

Palavras funcionais como *"de"*, *"que"*, *"com"* aparecem em milhares de definições e criariam hubs artificiais sem valor semântico. Foram removidas usando a lista de stopwords do spaCy para português, complementada por termos metalinguísticos comuns em definições de dicionário.

### Por que o Dicionário Aberto?

O Dicionário Aberto é baseado na obra clássica de Cândido de Figueiredo e mantido por Alberto Simões na Universidade do Minho. Ele oferece definições em XML puro e bem estruturado — sem necessidade de parsing de wikitext, sem API, sem compressão. O formato com arquivos separados por letra facilita o processamento incremental e a depuração isolada de subconjuntos do vocabulário.

---

## Dependências

| Biblioteca | Versão mínima | Função no projeto |
|---|---|---|
| `spacy` | 3.7 | Tokenização, remoção de stopwords e lematização (PLN) |
| `networkx` | 3.2 | Construção, manipulação e análise de topologia do grafo |
| `tqdm` | 4.66 | Barras de progresso no terminal |

```
# requirements.txt
spacy>=3.7
networkx>=3.2
tqdm>=4.66
```

```bash
pip install spacy networkx tqdm
python -m spacy download pt_core_news_lg
```

---

## Roadmap

- [ ] Visualização interativa do grafo com [Pyvis](https://pyvis.readthedocs.io/)
- [ ] Exportação para formato `.graphml` (compatível com Gephi e Cytoscape)
- [ ] Implementação de PageRank para ranking semântico alternativo ao In-Degree
- [ ] Interface web para consulta de caminhos mínimos
- [ ] Suporte a exportação para Neo4j (Cypher)
- [ ] Filtragem por classe gramatical (substantivos, verbos, adjetivos)

---

