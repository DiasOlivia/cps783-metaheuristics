import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def test_construtiva_aleatoria__viavel():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    solucao = binaria.construtiva_aleatoria(itens, capacidade)
    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade


def test_construtiva_gulosa__exemplo_do_guloso_por_densidade():
    pesos = [4, 3, 7, 5, 3, 2, 3]
    valores = [12, 8, 17, 11, 6, 2, 2]
    itens = [Item(p, v) for p, v in zip(pesos, valores)]
    assert binaria.construtiva_gulosa(itens, 9) == [1, 1, 0, 0, 0, 1, 0]


def test_construtiva_gulosa_aleatoria__alfa_zero_e_a_gulosa():
    pesos = [4, 3, 7, 5, 3, 2, 3]
    valores = [12, 8, 17, 11, 6, 2, 2]
    itens = [Item(p, v) for p, v in zip(pesos, valores)]
    gulosa = binaria.construtiva_gulosa(itens, 9)
    assert binaria.construtiva_gulosa_aleatoria(itens, 9, alfa=0) == gulosa


def test_construtiva_gulosa_aleatoria__alfa_um_viavel_e_maximal():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    for semente in range(5):
        random.seed(semente)
        solucao = binaria.construtiva_gulosa_aleatoria(itens, capacidade, alfa=1)
        _, peso = binaria.calcular_valor_peso(solucao, itens, capacidade)
        assert peso <= capacidade
        assert all(
            peso + item.peso > capacidade
            for item, bit in zip(itens, solucao)
            if not bit
        )


def test_construtiva_gulosa_aleatoria__vies_e_parametros():
    # Só cabe um item: com α = 1 os três estão na RCL, e o viés decide
    itens = [Item(1, 10), Item(1, 5), Item(1, 1)]

    def so_o_melhor(r):
        return 1.0 if r == 1 else 0.0

    for semente in range(5):
        random.seed(semente)
        escolhida = binaria.construtiva_gulosa_aleatoria(
            itens, 1, alfa=1, vies=so_o_melhor
        )
        assert escolhida == [1, 0, 0]
    with pytest.raises(ValueError):
        binaria.construtiva_gulosa_aleatoria(itens, 1, alfa=1.5)
    with pytest.raises(ValueError):
        binaria.construtiva_gulosa_aleatoria(itens, 1, vies="quadratica")
