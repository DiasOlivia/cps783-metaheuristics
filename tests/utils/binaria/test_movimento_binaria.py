import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def _instancia():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def test_gerar_vizinho__um_bit_viavel():
    itens, capacidade = _instancia()
    solucao = [0] * 20
    vizinho = binaria.gerar_vizinho(solucao, itens, capacidade)
    assert solucao == [0] * 20  # entrada não é modificada
    assert sum(a != b for a, b in zip(solucao, vizinho)) == 1
    assert binaria.calcular_valor_peso(vizinho, itens, capacidade)[1] <= capacidade


def test_gerar_vizinho__k_trocas_continuam_viaveis():
    itens, capacidade = _instancia()
    vizinho = [0] * 20
    for _ in range(50):
        vizinho = binaria.gerar_vizinho(vizinho, itens, capacidade, k=3)
        assert (
            binaria.calcular_valor_peso(vizinho, itens, capacidade)[1] <= capacidade
        )


def test_gerar_vizinho__sem_vizinho_viavel():
    with pytest.raises(ValueError):
        binaria.gerar_vizinho([0, 0], [Item(5, 1), Item(6, 1)], 4)
