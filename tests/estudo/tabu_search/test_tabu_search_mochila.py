"""Pytest tests for Tabu Search on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.estudo.tabu_search import tabu_search_mochila
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False

# Exemplo da aula: C = 23, pesos e benefícios dos objetos 1 a 5
ITENS_SLIDE = [Item(4, 2), Item(5, 2), Item(7, 3), Item(9, 4), Item(6, 4)]


def test_tabu_search_mochila__exemplo_do_slide():
    melhor, historico = tabu_search_mochila(
        ITENS_SLIDE,
        23,
        tamanho_tabu=1,
        max_sem_melhora=1,
        construtiva=lambda *_: [0, 1, 0, 1, 0],
    )

    assert melhor == [0, 0, 1, 1, 1]
    assert historico["valor_atual"] == {0: 6, 1: 10, 2: 8, 3: 11, 4: 7, 5: 9}
    assert historico["melhor_valor"][5] == 11
    assert historico["avaliacoes"][5] == 1 + 5 * 5


def test_tabu_search_mochila__instancia_de_referencia():
    """Benchmark the same 20-item seed-0 instance as the other schemes."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    melhor_solucao, historico = tabu_search_mochila(itens, capacidade)
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())
    ultima = max(historico["melhor_valor"])

    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][ultima]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert historico["avaliacoes"][ultima] == 1 + 20 * ultima
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_tabu_search_mochila__representacao_por_ordem():
    random.seed(0)
    itens = gerar_instancia_aleatoria(12, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    melhor_ordem, historico = tabu_search_mochila(
        itens,
        capacidade,
        max_sem_melhora=10,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        vizinhanca=ordem.vizinhanca_troca,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][max(historico["melhor_valor"])]


def test_aspiracao_por_objetivo_e_por_default():
    """Walk a fake neighborhood where both aspiration rules are needed."""
    valores = {"A": 5, "B": 3, "C": 1, "D": 9, "E": 4, "F": 1, "G": 8, "H": 0}
    vizinhancas = {
        "A": [("x", (0,), ["B"]), ("y", (1,), ["C"])],
        "B": [("x", (0,), ["D"]), ("y", (1,), ["E"])],
        "D": [("z", (2,), ["F"])],
        "F": [("z", (2,), ["G"]), ("w", (0,), ["H"])],
    }

    melhor, historico = tabu_search_mochila(
        [Item(1, 1)] * 3,
        3,
        tamanho_tabu=2,
        max_sem_melhora=1,
        avaliar=lambda solucao, *_: valores[solucao[0]],
        construtiva=lambda *_: ["A"],
        vizinhanca=lambda solucao, *_: vizinhancas[solucao[0]],
    )

    # 2: D é tabu (item 0), mas 9 supera o melhor (5): aspiração por objetivo.
    # 4: G e H são tabu e não superam o melhor; H sai da quarentena primeiro
    # (prazo 4 contra 5) e é escolhida, mesmo valendo menos: aspiração por default
    assert historico["valor_atual"] == {0: 5, 1: 3, 2: 9, 3: 1, 4: 0}
    assert melhor == ["D"]


def test_lista_tabu_dinamica():
    random.seed(1)
    itens = gerar_instancia_aleatoria(15, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    _, historico = tabu_search_mochila(
        itens, capacidade, tamanho_tabu=(2, 4), max_sem_melhora=30, tau=1
    )
    tamanhos = historico["tamanho_tabu"]

    assert set(tamanhos.values()) <= {2, 3, 4}
    # |T| só muda a cada τ·Tmax = 4 iterações
    assert all(tamanhos[t] == tamanhos[(t - 1) // 4 * 4 + 1] for t in tamanhos)


def test_valor_alvo_interrompe_a_busca():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    random.seed(0)
    _, historico = tabu_search_mochila(itens, capacidade, valor_alvo=valor_otimo)
    melhores = historico["melhor_valor"]
    ultima = max(melhores)

    assert melhores[ultima] == valor_otimo
    assert ultima == 0 or melhores[ultima - 1] < valor_otimo


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    for parametros in (
        {"tamanho_tabu": 0},
        {"tamanho_tabu": (5, 3)},
        {"max_sem_melhora": -1},
        {"tau": 0},
    ):
        with pytest.raises(ValueError):
            tabu_search_mochila(itens, 2, **parametros)
