import random

import pytest

from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica


def test_gerar_instancia_aleatoria__sorteia_peso_e_valor_de_cada_item():
    random.seed(7)
    itens = gerar_instancia_aleatoria(5, 20, 100)
    random.seed(7)
    esperado = [(random.randint(1, 20), random.randint(1, 100)) for _ in range(5)]
    assert [(item.peso, item.valor) for item in itens] == esperado


def test_gerar_instancia_aleatoria__correlacionada():
    random.seed(7)
    itens = gerar_instancia_aleatoria(50, 20, 100, correlacionada=True)
    assert all(item.valor == item.peso + 2 for item in itens)


def test_gerar_instancia_aleatoria__limites_invalidos():
    with pytest.raises(ValueError):
        gerar_instancia_aleatoria(3, 0, 10)


def test_programacao_dinamica__exemplo_do_guloso():
    pesos = [4, 3, 7, 5, 3, 2, 3]
    valores = [12, 8, 17, 11, 6, 2, 2]
    itens = [Item(p, v) for p, v in zip(pesos, valores)]
    assert programacao_dinamica(itens, 9) == (23, [1, 0, 0, 1, 0, 0, 0])
