"""Pytest tests for ILS on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.estudo.iterated_local_search import iterated_local_search_mochila
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False


def test_iterated_local_search_mochila__notebook_example():
    """Compare ILS with the exact optimum on one reproducible instance."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    melhor_solucao, historico = iterated_local_search_mochila(
        itens=itens,
        capacidade=capacidade,
        max_iteracoes=250,
        intensidade_perturbacao=4,
    )
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert len(historico["valor_candidato"]) == 251  # inclui a iteração 0
    assert len(historico["avaliacoes"]) == 251
    assert peso <= capacidade
    assert melhor_valor == max(melhores)
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_iterated_local_search_mochila__representacao_por_ordem():
    random.seed(0)
    itens = gerar_instancia_aleatoria(12, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    melhor_ordem, historico = iterated_local_search_mochila(
        itens,
        capacidade,
        max_iteracoes=10,
        intensidade_perturbacao=3,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        busca_local=ordem.busca_local_primeira_melhora,
        perturbacao=ordem.perturbar,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][10]


def test_caso_sem_itens_e_sem_iteracoes():
    solucao, historico = iterated_local_search_mochila([], 0, 0)
    assert solucao == []
    assert historico["melhor_valor"] == {0: 0}


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        iterated_local_search_mochila([Item(1, 2)], 4, 10, intensidade_perturbacao=2)
    with pytest.raises(ValueError):
        iterated_local_search_mochila([Item(1, 2)], 4, -1)
