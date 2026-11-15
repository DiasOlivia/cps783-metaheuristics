import random

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
