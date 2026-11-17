import random
from collections import Counter

import pytest

from metaheuristics.utils.selecao import selecao_classes
from metaheuristics.utils.selecao import selecao_ranking
from metaheuristics.utils.selecao import selecao_roleta
from metaheuristics.utils.selecao import selecao_torneio


def test_selecao_roleta__chances_do_slide_17():
    random.seed(0)
    sorteios = Counter(selecao_roleta([150, 50, 200, 100], 20000))
    chances = [sorteios[i] / 20000 for i in range(4)]
    assert chances == pytest.approx([0.3, 0.1, 0.4, 0.2], abs=0.01)


def test_selecao_roleta__valor_negativo_nao_tem_fatia():
    random.seed(0)
    assert set(selecao_roleta([-5, 0, 3], 100)) == {2}


def test_selecao_roleta__tudo_zero_e_uniforme():
    random.seed(0)
    assert set(selecao_roleta([0, -1, 0], 100)) == {0, 1, 2}


def test_selecao_ranking__peso_pela_posicao_e_nao_pelo_valor():
    random.seed(0)
    # o 2º tem aptidão 1000 vezes maior, mas só o dobro da chance do 1º
    sorteios = Counter(selecao_ranking([1, 1000], 30000))
    assert sorteios[1] / 30000 == pytest.approx(2 / 3, abs=0.01)


def test_selecao_torneio__q_grande_escolhe_o_melhor():
    random.seed(0)
    assert set(selecao_torneio([3, 9, 1, 4], 50, q=40)) == {1}


def test_selecao_torneio__q_1_e_aleatorio():
    random.seed(0)
    assert set(selecao_torneio([3, 9, 1, 4], 200, q=1)) == {0, 1, 2, 3}
    with pytest.raises(ValueError):
        selecao_torneio([1, 2], 1, q=0)


def test_selecao_classes__melhores_piores_e_sorteados():
    random.seed(0)
    valores = [5, 9, 1, 7, 3, 8, 2, 6, 4, 0]
    escolhidos = selecao_classes(valores, 10, melhores=0.2, piores=0.3)
    assert len(escolhidos) == 10
    assert escolhidos[:2] == [1, 5]  # os 2 melhores
    assert escolhidos[2:5] == [6, 2, 9]  # os 3 piores
    with pytest.raises(ValueError):
        selecao_classes(valores, 2, melhores=0.7, piores=0.4)


def test_selecao_classes__nunca_passa_da_quantidade():
    assert len(selecao_classes([1, 2, 3, 4], 3, melhores=0.5, piores=0.5)) == 3
