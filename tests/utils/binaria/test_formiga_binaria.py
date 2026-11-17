import random
from collections import Counter

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.feromonio import Feromonio
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def _instancia():
    random.seed(0)
    itens = gerar_instancia_aleatoria(15, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def test_construtiva_formiga__viavel_e_maximal():
    itens, capacidade = _instancia()
    random.seed(1)
    for _ in range(20):
        solucao = binaria.construtiva_formiga(itens, capacidade)
        _, peso = binaria.calcular_valor_peso(solucao, itens, capacidade)
        assert peso <= capacidade
        assert all(
            bit or peso + item.peso > capacidade for item, bit in zip(itens, solucao)
        )


def test_construtiva_formiga__q0_1_e_a_gulosa():
    itens, capacidade = _instancia()
    assert binaria.construtiva_formiga(
        itens, capacidade, q0=1
    ) == binaria.construtiva_gulosa(itens, capacidade)


def test_construtiva_formiga__primeiro_item_proporcional_a_tau_eta():
    # todos cabem no primeiro passo; η = 2, 1, 1 e τ = 1, 1, 2
    itens = [Item(1, 2), Item(1, 1), Item(1, 1)]
    feromonio = Feromonio(1.0)
    feromonio[2] = 2.0
    random.seed(0)
    primeiros = Counter(
        binaria.construtiva_formiga(itens, 1, feromonio).index(1)
        for _ in range(20000)
    )
    chances = [primeiros[j] / 20000 for j in range(3)]
    assert chances == pytest.approx([0.4, 0.2, 0.4], abs=0.015)


def test_construtiva_formiga__feromonio_alto_atrai():
    itens, capacidade = _instancia()
    feromonio = Feromonio(1.0)
    pouco_denso = min(
        range(len(itens)), key=lambda j: itens[j].valor / itens[j].peso
    )
    feromonio[pouco_denso] = 1000.0
    random.seed(1)
    com = sum(
        binaria.construtiva_formiga(itens, capacidade, feromonio)[pouco_denso]
        for _ in range(100)
    )
    sem = sum(
        binaria.construtiva_formiga(itens, capacidade)[pouco_denso]
        for _ in range(100)
    )
    assert com > sem


def test_trilha__os_itens_dentro():
    assert binaria.trilha([1, 0, 1, 1, 0], [], 0) == [0, 2, 3]
