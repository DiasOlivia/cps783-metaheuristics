# Metaheurísticas em Otimização Combinatória

Repositório de estudo sobre **heurísticas e metaheurísticas** para problemas de otimização combinatória. Cada algoritmo tem sua própria pasta, com a implementação em Python, um README explicando a teoria, um gráfico para visualizar o que está acontecendo e um teste com um exemplo.

## Conteúdo

| Pasta | Algoritmo | Problema |
|---|---|---|
| [`metaheuristics/`](metaheuristics/README.md) | Conceitos: representação e heurística × metaheurística | — |
| [`metaheuristics/estudo/guloso/`](metaheuristics/estudo/guloso/README.md) | Algoritmo guloso | — |
| [`metaheuristics/estudo/guloso/kruskal/`](metaheuristics/estudo/guloso/kruskal/README.md) | Kruskal | Árvore Geradora Mínima |
| [`metaheuristics/estudo/guloso/mochila/`](metaheuristics/estudo/guloso/mochila/README.md) | Heurísticas gulosas | Mochila 0-1 |
| [`metaheuristics/estudo/guloso/caixeiro_viajante/`](metaheuristics/estudo/guloso/caixeiro_viajante/README.md) | Heurística gulosa | Caixeiro Viajante |
| [`metaheuristics/estudo/simulated_annealing/`](metaheuristics/estudo/simulated_annealing/README.md) | Simulated Annealing | Mochila 0-1 |
| [`metaheuristics/estudo/iterated_local_search/`](metaheuristics/estudo/iterated_local_search/README.md) | Iterated Local Search | Mochila 0-1 |
| [`metaheuristics/estudo/variable_neighborhood_search/`](metaheuristics/estudo/variable_neighborhood_search/README.md) | Variable Neighborhood Search | Mochila 0-1 |
| [`metaheuristics/estudo/adaptive_large_neighborhood_search/`](metaheuristics/estudo/adaptive_large_neighborhood_search/README.md) | Adaptive Large Neighbourhood Search | Mochila 0-1 |
| [`metaheuristics/estudo/tabu_search/`](metaheuristics/estudo/tabu_search/README.md) | Busca Tabu | Mochila 0-1 |
| [`metaheuristics/estudo/grasp/`](metaheuristics/estudo/grasp/README.md) | GRASP + Path-Relinking | Mochila 0-1 |
| [`metaheuristics/estudo/particle_swarm_optimization/`](metaheuristics/estudo/particle_swarm_optimization/README.md) | Enxame de Partículas (PSO) | Mochila 0-1 |
| [`metaheuristics/estudo/genetic_algorithm/`](metaheuristics/estudo/genetic_algorithm/README.md) | Algoritmo Genético (AG) | Mochila 0-1 |
| [`metaheuristics/estudo/ant_colony_optimization/`](metaheuristics/estudo/ant_colony_optimization/README.md) | Colônia de Formigas (ACO) | Mochila 0-1 |
| [`metaheuristics/utils/`](metaheuristics/utils/README.md) | Peças trocáveis do SA, ILS, VNS, ALNS, Busca Tabu, GRASP, PSO, AG e ACO, gráficos e depurador visual | Mochila 0-1 |
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
└── estudo/            algoritmos das aulas
    └── <algoritmo>/
        ├── __init__.py    implementação
        ├── plot.py        gráficos (no guloso)
        └── README.md      teoria e exemplos
tests/
└── estudo/
    └── <algoritmo>/   um teste por função, espelhando a estrutura acima
```
