"""Pytest tests for Basic VNS on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico
from metaheuristics.variable_neighborhood_search import (
    variable_neighborhood_search_mochila,
)

PLOT = False


def test_variable_neighborhood_search_mochila__notebook_example():
    """Benchmark the same 20-item seed-0 instance as SA and ILS."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)
    melhor_solucao, historico = variable_neighborhood_search_mochila(
        itens=itens, capacidade=capacidade, max_iteracoes=250, k_max=4
    )
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert len(historico["valor_candidato"]) == 251
    assert len(historico["k"]) == 251
    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][250]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_variable_neighborhood_search_mochila__representacao_por_ordem():
    random.seed(0)
    itens = gerar_instancia_aleatoria(12, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    melhor_ordem, historico = variable_neighborhood_search_mochila(
        itens,
        capacidade,
        max_iteracoes=10,
        k_max=3,
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


def test_caso_vazio_e_zero_iteracoes():
    solucao, historico = variable_neighborhood_search_mochila([], 0, 0)
    assert solucao == []
    assert historico["melhor_valor"] == {0: 0}
    solucao, historico = variable_neighborhood_search_mochila([], 0, 3)
    assert len(historico["melhor_valor"]) == 4


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], 4, 10, k_max=2)
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], 4, -1, k_max=1)
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], -1, 10, k_max=1)


def test_melhoria_reinicia_vizinhanca():
    """Verify the reset-to-N1 rule with deterministic fake pieces."""
    itens = [Item(1, 1), Item(1, 2), Item(1, 3)]
    usados = []

    def perturbacao_falsa(solucao, itens, capacidade, k, debug=None):
        usados.append(k)
        return solucao

    candidatos = iter([[1, 0, 0], [0, 1, 0], [0, 1, 0]])
    _, historico = variable_neighborhood_search_mochila(
        itens,
        1,
        3,
        3,
        construtiva=lambda *_: [1, 0, 0],
        perturbacao=perturbacao_falsa,
        busca_local=lambda *_, **__: (next(candidatos), 0),
    )

    assert usados == [1, 2, 1]
    assert list(historico["k"].values()) == [0, 1, 2, 1]
    assert list(historico["valor_atual"].values()) == [1, 1, 2, 2]
