"""Pytest tests for ALNS on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.estudo.adaptive_large_neighborhood_search import (
    adaptive_large_neighborhood_search_mochila,
)
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.aceitacao import temperaturas
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False


def test_adaptive_large_neighborhood_search_mochila__notebook_example():
    """Benchmark the same 20-item seed-0 instance as SA, ILS and VNS."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)
    total = len(temperaturas(100, 1, 0.99))

    melhor_solucao, historico = adaptive_large_neighborhood_search_mochila(
        itens, capacidade, 100, 1, 0.99
    )
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert len(historico["valor_candidato"]) == total + 1  # inclui a iteração 0
    assert len(historico["peso remocao_shaw"]) == total + 1
    assert len(historico["temperatura"]) == total
    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][total]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_adaptive_large_neighborhood_search_mochila__representacao_por_ordem():
    random.seed(0)
    itens = gerar_instancia_aleatoria(12, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    total = len(temperaturas(100, 1, 0.97))

    melhor_ordem, historico = adaptive_large_neighborhood_search_mochila(
        itens,
        capacidade,
        100,
        1,
        0.97,
        remocoes=(ordem.remocao_aleatoria, ordem.remocao_pior, ordem.remocao_shaw),
        insercoes=(
            ordem.insercao_aleatoria,
            ordem.insercao_gulosa,
            ordem.insercao_arrependimento,
        ),
        tamanho_segmento=20,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][total]
    assert "peso insercao_arrependimento" in historico


def test_pontuacoes_e_pesos_do_segmento():
    """Score each case once with deterministic fake operators."""
    itens = [Item(1, 1), Item(1, 2), Item(1, 3)]
    candidatos = iter([[0, 0, 1], [1, 0, 0], [0, 1, 0], [1, 0, 0]])

    def remover(solucao, itens, capacidade, k, debug=None):
        return solucao

    def inserir(solucao, itens, capacidade, debug=None):
        return next(candidatos)

    # Temperaturas 8, 4, 2 e 1: quatro iterações, um segmento
    _, historico = adaptive_large_neighborhood_search_mochila(
        itens,
        3,
        8,
        0.5,
        0.5,
        remocoes=(remover,),
        insercoes=(inserir,),
        tamanho_segmento=4,
        fator_reacao=0.5,
        construtiva=lambda *_: [0, 0, 0],
        aceitacao=lambda delta, iteracao: True,
    )

    # 3 (novo melhor: 33), 1 (piora nova: 9), 2 (melhora nova: 13) e 1 de novo
    # (piora já encontrada: rejeitada mesmo com uma aceitação que aceita tudo)
    assert list(historico["valor_atual"].values()) == [0, 3, 1, 2, 2]
    pontos, usos = 33 + 9 + 13 + 0, 4
    peso = (1 - 0.5) * 1 + 0.5 * pontos / usos
    assert historico["peso remover"] == {0: 1, 1: 1, 2: 1, 3: 1, 4: peso}
    assert historico["peso inserir"][4] == peso


def test_perturbacao_entra_como_remocao():
    random.seed(0)
    itens = gerar_instancia_aleatoria(10, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    solucao, historico = adaptive_large_neighborhood_search_mochila(
        itens,
        capacidade,
        50,
        1,
        0.9,
        remocoes=(binaria.remocao_shaw, binaria.perturbar),
        tamanho_segmento=10,
    )

    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade
    assert "peso perturbar" in historico


def test_agenda_vazia():
    itens = [Item(2, 3), Item(3, 4)]
    solucao, historico = adaptive_large_neighborhood_search_mochila(
        itens, 4, 1, 1, 0.5, construtiva=lambda *_: [1, 0]
    )
    assert solucao == [1, 0]
    assert historico["melhor_valor"] == {0: 3}
    _, historico = adaptive_large_neighborhood_search_mochila([], 0, 1, 1, 0.5)
    assert historico["melhor_valor"] == {0: 0}


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    invalidos = [
        {"grau_remocao": 0},
        {"grau_remocao": 1.5},
        {"tamanho_segmento": 0},
        {"fator_reacao": 2},
        {"remocoes": ()},
        {"insercoes": ()},
        {"remocoes": (binaria.remocao_pior, binaria.remocao_pior)},
    ]
    for parametros in invalidos:
        with pytest.raises(ValueError):
            adaptive_large_neighborhood_search_mochila(
                itens, 2, 10, 1, 0.5, **parametros
            )
