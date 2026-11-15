import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item


def test_perturbar__repara_e_mantem_viabilidade():
    random.seed(3)
    itens = [Item(4, 6), Item(5, 8), Item(3, 5), Item(2, 2)]
    inicial = [1, 0, 1, 0]
    perturbada = binaria.perturbar(inicial, itens, 7, 3)
    assert binaria.calcular_valor_peso(perturbada, itens, 7)[1] <= 7
    assert inicial == [1, 0, 1, 0]


def test_perturbar__distancia_exata_quando_nao_precisa_reparar():
    random.seed(4)
    itens = [Item(1, 2) for _ in range(8)]
    solucao = [0] * 8
    perturbada = binaria.perturbar(solucao, itens, 8, 3)
    assert sum(a != b for a, b in zip(solucao, perturbada)) == 3


def test_perturbar__entradas_invalidas():
    itens = [Item(4, 6), Item(5, 8)]
    with pytest.raises(ValueError):
        binaria.perturbar([1, 0], itens, 7, 3)
    with pytest.raises(ValueError):
        binaria.perturbar([1, 1], itens, 7, 1)
