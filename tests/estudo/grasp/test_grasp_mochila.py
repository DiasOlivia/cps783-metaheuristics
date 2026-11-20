"""Pytest tests for GRASP with path-relinking on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.estudo.grasp import grasp_mochila
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


def test_grasp_mochila__instancia_de_referencia():
    """Benchmark the same 20-item seed-0 instance as the other schemes."""
    itens, capacidade = _instancia()
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    random.seed(1)
    melhor_solucao, historico = grasp_mochila(itens, capacidade)
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert sorted(historico["valor_atual"]) == list(range(1, 51))
    assert set(historico["alfa"].values()) == {0.3}
    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][50]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_grasp_puro_e_reativo():
    itens, capacidade = _instancia()
    alfas = (0.1, 0.5, 0.9)

    random.seed(1)
    solucao, _ = grasp_mochila(itens, capacidade, max_iteracoes=20, reconexao=None)
    random.seed(1)
    _, historico = grasp_mochila(itens, capacidade, max_iteracoes=30, alfa=alfas)

    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade
    assert set(historico["alfa"].values()) <= set(alfas)


def test_hashing_nao_muda_o_resultado_e_economiza_avaliacoes():
    itens, capacidade = _instancia()
    execucoes = {}
    for hashing in (True, False):
        random.seed(2)
        execucoes[hashing] = grasp_mochila(
            itens, capacidade, max_iteracoes=30, hashing=hashing
        )

    (com, historico_com), (sem, historico_sem) = execucoes[True], execucoes[False]
    assert com == sem
    assert historico_com["valor_atual"] == historico_sem["valor_atual"]
    assert historico_com["avaliacoes"][30] < historico_sem["avaliacoes"][30]


def test_reconexao_melhora_a_solucao_da_iteracao():
    """Relink a fixed second construction with the elite of the first one."""
    construcoes = iter([[1, 1, 1, 1], [0, 0, 0, 0]])

    def avaliar(solucao, *_):
        return 10 if solucao == [1, 1, 0, 0] else sum(solucao)

    melhor, historico = grasp_mochila(
        [Item(1, 1)] * 4,
        4,
        max_iteracoes=2,
        direcao="forward",
        avaliar=avaliar,
        construtiva=lambda *_: next(construcoes),
        busca_local=None,
    )

    # 2: a construída vale 0; o PR até a elite (1111) passa por (1100), que vale 10
    assert historico["valor_candidato"] == {1: 4, 2: 0}
    assert historico["valor_atual"] == {1: 4, 2: 10}
    assert melhor == [1, 1, 0, 0]


def test_grasp_mochila__representacao_por_ordem():
    itens, capacidade = _instancia(12)

    random.seed(1)
    melhor_ordem, historico = grasp_mochila(
        itens,
        capacidade,
        max_iteracoes=10,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_gulosa_aleatoria,
        busca_local=ordem.busca_local_primeira_melhora,
        reconexao=ordem.passos_para_guia,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][10]


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    for parametros in (
        {"alfa": 1.5},
        {"alfa": ()},
        {"max_iteracoes": 0},
        {"tamanho_elite": 0},
        {"diferenca_minima": -1},
        {"periodo_reativo": 0},
        {"periodo_reconexao": 0},
        {"direcao": "lateral"},
    ):
        with pytest.raises(ValueError):
            grasp_mochila(itens, 2, **parametros)
