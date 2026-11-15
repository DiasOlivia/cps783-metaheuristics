import random

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item

ITENS = [
    Item(4, 12),
    Item(3, 8),
    Item(7, 17),
    Item(5, 11),
    Item(3, 6),
    Item(2, 2),
    Item(3, 3),
]


def test_insercoes__mantem_o_que_esta_dentro_e_enchem_a_mochila():
    random.seed(1)
    parcial = [1, 0, 0, 0, 0, 0, 0]
    for insercao in (binaria.insercao_aleatoria, binaria.insercao_gulosa):
        nova = insercao(parcial, ITENS, 9)
        _, peso = binaria.calcular_valor_peso(nova, ITENS, 9)
        assert nova[0] == 1
        assert peso <= 9
        assert all(peso + item.peso > 9 for item, bit in zip(ITENS, nova) if not bit)
    assert parcial == [1, 0, 0, 0, 0, 0, 0]


def test_insercao_gulosa__entra_o_item_de_maior_valor_que_cabe():
    # Com o item 0 dentro sobram 5 de capacidade; dos que cabem, o item 3 (5/11)
    # tem o maior valor e enche a mochila. Por densidade, entrariam 1 e 5 (valor 22)
    nova = binaria.insercao_gulosa([1, 0, 0, 0, 0, 0, 0], ITENS, 9)
    assert nova == [1, 0, 0, 1, 0, 0, 0]
    assert binaria.avaliar(nova, ITENS, 9) == 23
