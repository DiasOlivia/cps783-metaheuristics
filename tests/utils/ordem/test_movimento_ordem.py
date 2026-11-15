import random

from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item

ITENS = [Item(1, 1) for _ in range(6)]


def test_gerar_vizinho__troca_duas_posicoes():
    random.seed(0)
    solucao = list(range(6))
    nova = ordem.gerar_vizinho(solucao, ITENS, 3)
    assert solucao == list(range(6))  # entrada não é modificada
    assert sorted(nova) == list(range(6))
    assert sum(a != b for a, b in zip(solucao, nova)) == 2


def test_gerar_vizinho__k_trocas_continuam_permutacao():
    random.seed(0)
    nova = ordem.gerar_vizinho(list(range(6)), ITENS, 3, k=4)
    assert sorted(nova) == list(range(6))
