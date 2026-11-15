import random

from metaheuristics.utils import ordem
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
# Com C = 9, esta ordem decodifica para os itens 0 e 3
SOLUCAO = [0, 3, 1, 2, 4, 5, 6]


def test_remocoes__tiram_da_ordem_itens_que_estavam_na_mochila():
    random.seed(0)
    for remocao in (ordem.remocao_aleatoria, ordem.remocao_pior, ordem.remocao_shaw):
        parcial = remocao(SOLUCAO, ITENS, 9, 1)
        removidos = set(SOLUCAO) - set(parcial)
        assert len(parcial) == 6
        assert removidos <= {0, 3}
        assert parcial == [i for i in SOLUCAO if i not in removidos]
    assert SOLUCAO == [0, 3, 1, 2, 4, 5, 6]


def test_remocao_pior__tira_o_item_decodificado_de_menor_densidade():
    assert ordem.remocao_pior(SOLUCAO, ITENS, 9, 1) == [0, 1, 2, 4, 5, 6]
