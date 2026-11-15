# Metaheurísticas em Otimização Combinatória

Repositório de estudo sobre **heurísticas e metaheurísticas** para problemas de otimização combinatória. Cada algoritmo tem sua própria pasta, com a implementação em Python, um README explicando a teoria, um gráfico para visualizar o que está acontecendo e um teste com um exemplo.

## Conteúdo

| Pasta | Algoritmo | Problema |
|---|---|---|
| [`metaheuristics/`](metaheuristics/README.md) | Conceitos: representação e heurística × metaheurística | — |
| [`metaheuristics/guloso/`](metaheuristics/guloso/README.md) | Algoritmo guloso | — |
| [`metaheuristics/guloso/kruskal/`](metaheuristics/guloso/kruskal/README.md) | Kruskal | Árvore Geradora Mínima |
| [`metaheuristics/guloso/mochila/`](metaheuristics/guloso/mochila/README.md) | Heurísticas gulosas | Mochila 0-1 |
| [`metaheuristics/guloso/caixeiro_viajante/`](metaheuristics/guloso/caixeiro_viajante/README.md) | Heurística gulosa | Caixeiro Viajante |
| [`metaheuristics/simulated_annealing/`](metaheuristics/simulated_annealing/README.md) | Simulated Annealing | Mochila 0-1 |
| [`metaheuristics/iterated_local_search/`](metaheuristics/iterated_local_search/README.md) | Iterated Local Search | Mochila 0-1 |
| [`metaheuristics/variable_neighborhood_search/`](metaheuristics/variable_neighborhood_search/README.md) | Variable Neighborhood Search | Mochila 0-1 |
| [`metaheuristics/utils/`](metaheuristics/utils/README.md) | Peças trocáveis do SA, ILS e VNS, gráficos e depurador visual | Mochila 0-1 |
| [`metaheuristics/laboratorio.ipynb`](metaheuristics/laboratorio.ipynb) | Notebook para montar e comparar combinações | Mochila 0-1 |

## Instalação

Requer Python 3.11 e [Poetry](https://python-poetry.org/).

```bash
conda create -p ./venv python=3.11
conda activate ./venv
poetry install
```

## Como usar

Rodar os testes:

```bash
pytest
```

Os testes reproduzem os exemplos de cada README. Com `PLOT = True` no arquivo de teste, os gráficos são salvos em `plots/`, que não vai para o git.

Para experimentar com as metaheurísticas (trocar peças, comparar combinações e ver cada etapa da busca), abra o [notebook do laboratório](metaheuristics/laboratorio.ipynb) com o kernel do ambiente do Poetry. As peças estão descritas em [`metaheuristics/utils/`](metaheuristics/utils/README.md).

## Estrutura

```text
metaheuristics/
├── README.md          conceitos: representação, heurística × metaheurística
├── laboratorio.ipynb  notebook para combinar as peças
├── utils/             peças trocáveis, histórico, gráficos e depurador
│   ├── binaria/       peças da representação binária
│   └── ordem/         peças da representação por ordem
└── <algoritmo>/
    ├── __init__.py    implementação
    ├── plot.py        gráficos (no guloso)
    └── README.md      teoria e exemplos
tests/
└── <algoritmo>/       um teste por função, espelhando a estrutura acima
```
