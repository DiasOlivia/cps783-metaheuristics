import random

from metaheuristics.utils import binaria


def test_coordenadas__os_bits():
    assert binaria.coordenadas([1, 0, 1], [], 0) == [1.0, 0.0, 1.0]


def test_mover_sigmoide__velocidade_extrema_fixa_o_bit():
    random.seed(0)
    solucao = [0, 1, 0]
    for _ in range(20):
        assert binaria.mover_sigmoide(solucao, [], 0, [50, -50, 50]) == [1, 0, 1]
    assert solucao == [0, 1, 0]


def test_mover_sigmoide__velocidade_nula_e_cara_ou_coroa():
    random.seed(0)
    uns = sum(
        sum(binaria.mover_sigmoide([0] * 10, [], 0, [0.0] * 10)) for _ in range(100)
    )
    assert 400 < uns < 600
