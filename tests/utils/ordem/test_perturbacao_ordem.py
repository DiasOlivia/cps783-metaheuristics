import random

import pytest

from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item

ITENS = [Item(1, 1) for _ in range(10)]


def test_perturbar__mexe_no_maximo_em_k_posicoes():
    random.seed(2)
    solucao = list(range(10))
    nova = ordem.perturbar(solucao, ITENS, 5, 4)
    assert solucao == list(range(10))  # entrada não é modificada
    assert sorted(nova) == list(range(10))
    assert sum(a != b for a, b in zip(solucao, nova)) <= 4


def test_perturbar__k_invalido():
    with pytest.raises(ValueError):
        ordem.perturbar(list(range(10)), ITENS, 5, 11)
