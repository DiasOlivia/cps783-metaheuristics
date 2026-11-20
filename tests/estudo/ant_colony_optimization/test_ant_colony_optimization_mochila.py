"""Pytest tests for ACO on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.estudo.ant_colony_optimization import (
    ant_colony_optimization_mochila,
)
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False


def _instancia(n=20):
    random.seed(0)
    itens = gerar_instancia_aleatoria(n, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def test_ant_colony_optimization_mochila__instancia_de_referencia():
    """Benchmark the same 20-item seed-0 instance as the other schemes."""
    itens, capacidade = _instancia()
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    random.seed(1)
    melhor_solucao, historico = ant_colony_optimization_mochila(itens, capacidade)
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    iteracoes = sorted(historico["melhor_valor"])
    melhores = [historico["melhor_valor"][t] for t in iteracoes]

    assert iteracoes[0] == 1
    assert historico["avaliacoes"][iteracoes[-1]] == 20 * len(iteracoes)
    assert peso <= capacidade
    assert melhor_valor == melhores[-1]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert all(1 <= d <= 20 for d in historico["distintos"].values())
    assert gap <= 1

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_para_depois_de_max_sem_melhora():
    itens, capacidade = _instancia()
    random.seed(1)
    _, historico = ant_colony_optimization_mochila(
        itens, capacidade, max_sem_melhora=7
    )
    melhores = historico["melhor_valor"]
    ultima = max(melhores)
    ultima_melhora = min(t for t in melhores if melhores[t] == melhores[ultima])
    assert ultima - ultima_melhora == 7


@pytest.mark.parametrize(
    "parametros",
    [
        {"deposito": "elitista"},
        {"deposito": "ranking", "w": 3},
        {"deposito": "melhor", "q0": 0.9, "atualizacao_local": 0.1},
        {"alfa": 0},
    ],
)
def test_variantes(parametros):
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = ant_colony_optimization_mochila(
        itens, capacidade, max_sem_melhora=10, **parametros
    )
    valor, peso = binaria.calcular_valor_peso(solucao, itens, capacidade)
    assert peso <= capacidade
    assert valor == max(historico["melhor_valor"].values())


def test_busca_local_em_cada_formiga():
    itens, capacidade = _instancia()
    random.seed(1)
    _, historico = ant_colony_optimization_mochila(
        itens,
        capacidade,
        numero_formigas=5,
        max_sem_melhora=2,
        busca_local=binaria.busca_local_primeira_melhora,
    )
    ultima = max(historico["avaliacoes"])
    assert historico["avaliacoes"][ultima] > 5 * ultima


def test_ant_colony_optimization_mochila__representacao_por_ordem():
    itens, capacidade = _instancia(12)

    random.seed(1)
    melhor_ordem, historico = ant_colony_optimization_mochila(
        itens,
        capacidade,
        max_sem_melhora=20,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_formiga,
        trilha=ordem.trilha,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == max(historico["melhor_valor"].values())


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    for parametros in (
        {"numero_formigas": 0},
        {"max_sem_melhora": 0},
        {"evaporacao": 0},
        {"atualizacao_local": 1},
        {"q0": 1.5},
        {"beta": -1},
        {"feromonio_inicial": 0},
        {"deposito": "nenhum"},
        {"w": 1},
    ):
        with pytest.raises(ValueError):
            ant_colony_optimization_mochila(itens, 2, **parametros)
