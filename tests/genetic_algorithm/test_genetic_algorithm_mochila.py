"""Pytest tests for the Genetic Algorithm on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.genetic_algorithm import genetic_algorithm_mochila
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


def test_genetic_algorithm_mochila__instancia_de_referencia():
    """Benchmark the same 20-item seed-0 instance as the other schemes."""
    itens, capacidade = _instancia()
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    random.seed(1)
    melhor_solucao, historico = genetic_algorithm_mochila(itens, capacidade)
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert sorted(historico["valor_atual"]) == list(range(101))
    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][100]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert all(1 <= d <= 50 for d in historico["distintos"].values())
    assert gap <= 1

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_elitismo__o_melhor_da_populacao_nunca_piora():
    itens, capacidade = _instancia()
    random.seed(1)
    _, historico = genetic_algorithm_mochila(
        itens, capacidade, max_geracoes=30, reparo=None, avaliar=binaria.avaliar
    )
    atuais = list(historico["valor_atual"].values())

    assert all(b >= a for a, b in itertools.pairwise(atuais))
    assert all(
        historico["melhor_valor"][g] >= historico["valor_atual"][g]
        for g in historico["valor_atual"]
    )


def test_avaliacoes__uma_por_filho():
    itens, capacidade = _instancia()
    random.seed(1)
    # com Pc = 1 e Pm = 0, cada geração tem exatamente p filhos
    _, historico = genetic_algorithm_mochila(
        itens,
        capacidade,
        tamanho_populacao=10,
        max_geracoes=5,
        prob_cruzamento=1,
        prob_mutacao=0,
    )
    assert historico["avaliacoes"][5] == 10 + 5 * 10


def test_sem_reparo_com_avaliacao_penalizada():
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = genetic_algorithm_mochila(
        itens,
        capacidade,
        max_geracoes=30,
        reparo=None,
        avaliar=binaria.avaliar_penalizada,
    )
    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade
    assert historico["melhor_valor"][30] > 0


def test_busca_local_em_cada_filho():
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = genetic_algorithm_mochila(
        itens,
        capacidade,
        tamanho_populacao=10,
        max_geracoes=3,
        prob_cruzamento=1,
        prob_mutacao=0,
        busca_local=binaria.busca_local_primeira_melhora,
    )
    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade
    assert historico["avaliacoes"][3] > 10 + 3 * 10


def test_genetic_algorithm_mochila__representacao_por_ordem():
    itens, capacidade = _instancia(12)

    random.seed(1)
    melhor_ordem, historico = genetic_algorithm_mochila(
        itens,
        capacidade,
        max_geracoes=20,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        cruzamento=ordem.cruzamento_lox,
        mutacao=ordem.mutacao_inversao,
        reparo=None,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][20]


def test_zero_geracoes_devolve_o_melhor_individuo_inicial():
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = genetic_algorithm_mochila(itens, capacidade, max_geracoes=0)
    assert list(historico["melhor_valor"]) == [0]
    assert (
        binaria.avaliar(solucao, itens, capacidade) == historico["melhor_valor"][0]
    )


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    for parametros in (
        {"tamanho_populacao": 1},
        {"max_geracoes": -1},
        {"prob_cruzamento": 1.5},
        {"prob_mutacao": -0.1},
        {"tamanho_elite": 51},
    ):
        with pytest.raises(ValueError):
            genetic_algorithm_mochila(itens, 2, **parametros)
