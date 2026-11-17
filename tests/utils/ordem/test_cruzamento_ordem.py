import random

import pytest

from metaheuristics.utils import ordem

PAI1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
PAI2 = [9, 3, 7, 8, 2, 6, 5, 1, 4, 0]


def test_cruzamento_opx__slide_29():
    filho, _ = ordem.cruzamento_opx(PAI1, PAI2, [], 0, corte=5)
    assert filho == [1, 2, 3, 4, 5, 9, 7, 8, 6, 0]


def test_cruzamento_lox__slide_30():
    filho, _ = ordem.cruzamento_lox(PAI1, PAI2, [], 0, cortes=(3, 7))
    assert filho == [9, 3, 8, 4, 5, 6, 7, 2, 1, 0]


def test_cruzamento_pmx__slide_31():
    filho, _ = ordem.cruzamento_pmx(PAI1, PAI2, [], 0, cortes=(3, 7))
    assert filho == [9, 3, 2, 4, 5, 6, 7, 1, 8, 0]


def test_cruzamento_pmx__slide_32_gera_dois_filhos():
    # o "filho2" do slide mantém o trecho do pai 1; o "filho1", o do pai 2
    filhos = ordem.cruzamento_pmx(
        [1, 2, 3, 4, 5, 6], [2, 3, 5, 6, 1, 4], [], 0, cortes=(2, 5)
    )
    assert filhos == ([2, 1, 3, 4, 5, 6], [3, 2, 5, 6, 1, 4])


@pytest.mark.parametrize(
    "cruzamento",
    [ordem.cruzamento_opx, ordem.cruzamento_lox, ordem.cruzamento_pmx],
)
def test_cruzamento__filhos_sao_permutacoes(cruzamento):
    random.seed(0)
    pai1, pai2 = list(range(12)), list(range(12))
    random.shuffle(pai2)
    copias = (list(pai1), list(pai2))
    for _ in range(30):
        for filho in cruzamento(pai1, pai2, [], 0):
            assert sorted(filho) == list(range(12))
    assert (pai1, pai2) == copias


def test_cruzamento__cortes_invalidos():
    with pytest.raises(ValueError):
        ordem.cruzamento_opx(PAI1, PAI2, [], 0, corte=0)
    with pytest.raises(ValueError):
        ordem.cruzamento_lox(PAI1, PAI2, [], 0, cortes=(5, 5))
