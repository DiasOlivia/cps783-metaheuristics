import random

import pytest

from metaheuristics.utils import binaria


def test_cruzamento_um_ponto__slide_25():
    filhos = binaria.cruzamento_um_ponto(
        [1, 1, 0, 1, 0, 1], [1, 0, 0, 1, 0, 0], [], 0, corte=2
    )
    assert filhos == ([1, 1, 0, 1, 0, 0], [1, 0, 0, 1, 0, 1])


def test_cruzamento_multiponto__slide_26():
    filhos = binaria.cruzamento_multiponto(
        [0, 1, 1, 1, 0, 1], [1, 0, 0, 0, 1, 0], [], 0, cortes=[1, 2, 4]
    )
    assert filhos == ([0, 0, 1, 1, 1, 0], [1, 1, 0, 0, 0, 1])


def test_cruzamento_uniforme__slide_28():
    filhos = binaria.cruzamento_uniforme(
        [0, 1, 1, 1, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [],
        0,
        mascara=[1, 0, 0, 1, 0, 1, 1, 0],
    )
    assert filhos == ([1, 1, 1, 0, 0, 0, 1, 0], [0, 1, 0, 1, 0, 1, 1, 1])


@pytest.mark.parametrize(
    "cruzamento",
    [
        binaria.cruzamento_um_ponto,
        binaria.cruzamento_multiponto,
        binaria.cruzamento_uniforme,
    ],
)
def test_cruzamento__filhos_repartem_os_genes_dos_pais(cruzamento):
    random.seed(0)
    pai1 = [random.randint(0, 1) for _ in range(12)]
    pai2 = [random.randint(0, 1) for _ in range(12)]
    copias = (list(pai1), list(pai2))
    for _ in range(20):
        filho1, filho2 = cruzamento(pai1, pai2, [], 0)
        assert all(
            {a, b} == {f, g} for a, b, f, g in zip(pai1, pai2, filho1, filho2)
        )
    assert (pai1, pai2) == copias


def test_cruzamento__cortes_invalidos():
    with pytest.raises(ValueError):
        binaria.cruzamento_um_ponto([0, 1, 0], [1, 0, 1], [], 0, corte=3)
    with pytest.raises(ValueError):
        binaria.cruzamento_multiponto([0, 1, 0], [1, 0, 1], [], 0, cortes=3)
    with pytest.raises(ValueError):
        binaria.cruzamento_uniforme([0, 1, 0], [1, 0, 1], [], 0, mascara=[1, 0])
