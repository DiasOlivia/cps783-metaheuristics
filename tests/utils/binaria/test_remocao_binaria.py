import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item

# Densidades valor/peso: 3,0 · 2,67 · 2,43 · 2,2 · 2,0 · 1,0 · 1,0
ITENS = [
    Item(4, 12),
    Item(3, 8),
    Item(7, 17),
    Item(5, 11),
    Item(3, 6),
    Item(2, 2),
    Item(3, 3),
]
REMOCOES = (binaria.remocao_aleatoria, binaria.remocao_pior, binaria.remocao_shaw)


def test_remocoes__tiram_k_itens_de_dentro_sem_alterar_a_entrada():
    random.seed(0)
    solucao = [1, 1, 0, 1, 0, 1, 1]
    for remocao in REMOCOES:
        parcial = remocao(solucao, ITENS, 20, 2)
        assert sum(parcial) == 3
        assert all(antes >= depois for antes, depois in zip(solucao, parcial))
    assert solucao == [1, 1, 0, 1, 0, 1, 1]


def test_remocoes__k_maior_que_o_numero_de_itens_dentro_esvazia_a_mochila():
    random.seed(0)
    for remocao in REMOCOES:
        assert remocao([1, 0, 1, 0, 0, 0, 0], ITENS, 20, 5) == [0] * 7
        assert remocao([0] * 7, ITENS, 20, 2) == [0] * 7


def test_remocao_pior__tira_as_menores_densidades():
    # dentro: 0 (3,0), 1 (2,67), 3 (2,2), 5 (1,0) e 6 (1,0)
    solucao = [1, 1, 0, 1, 0, 1, 1]
    assert binaria.remocao_pior(solucao, ITENS, 20, 3) == [1, 1, 0, 0, 0, 0, 0]


def test_remocao_shaw__tira_a_semente_e_os_mais_parecidos():
    # Dois grupos de itens parecidos: {0, 1} e {2, 3}
    itens = [Item(10, 50), Item(10, 52), Item(1, 2), Item(1, 3)]
    for semente in range(10):
        random.seed(semente)
        parcial = binaria.remocao_shaw([1, 1, 1, 1], itens, 22, 2)
        removidos = {i for i, bit in enumerate(parcial) if not bit}
        assert removidos in ({0, 1}, {2, 3})


def test_remocoes__k_invalido():
    for remocao in REMOCOES:
        with pytest.raises(ValueError):
            remocao([1, 0, 0, 0, 0, 0, 0], ITENS, 20, 0)
