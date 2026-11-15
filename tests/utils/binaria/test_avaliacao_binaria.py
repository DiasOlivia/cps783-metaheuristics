import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item

ITENS = [Item(4, 12), Item(3, 8), Item(7, 17)]


def test_calcular_valor_peso__valor_zero_quando_passa_da_capacidade():
    assert binaria.calcular_valor_peso([1, 1, 0], ITENS, 9) == (20, 7)
    assert binaria.calcular_valor_peso([1, 1, 1], ITENS, 9) == (0, 14)


def test_calcular_valor_peso__solucao_invalida():
    with pytest.raises(ValueError):
        binaria.calcular_valor_peso([1, 2, 0], ITENS, 9)
    with pytest.raises(ValueError):
        binaria.calcular_valor_peso([1, 0], ITENS, 9)


def test_avaliar__so_o_valor():
    assert binaria.avaliar([1, 1, 0], ITENS, 9) == 20
