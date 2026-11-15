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
INSERCOES = (
    ordem.insercao_aleatoria,
    ordem.insercao_gulosa,
    ordem.insercao_arrependimento,
)


def test_insercoes__completam_a_ordem_sem_mudar_a_parcial():
    random.seed(0)
    parcial = [1, 2, 4, 5, 6]
    for insercao in INSERCOES:
        nova = insercao(parcial, ITENS, 9)
        assert sorted(nova) == list(range(7))
        assert [i for i in nova if i in parcial] == parcial
    assert parcial == [1, 2, 4, 5, 6]


def test_insercao_gulosa__recoloca_os_itens_na_melhor_posicao():
    # Faltam os itens 0 e 3; a melhor solução com C = 9 tem os dois (valor 23)
    nova = ordem.insercao_gulosa([1, 2, 4, 5, 6], ITENS, 9)
    assert ordem.avaliar(nova, ITENS, 9) == 23


def test_insercao_arrependimento__primeiro_o_item_que_mais_perde_se_adiado():
    # Na ordem [2], o item 0 vale 10 antes do 2 e 3 depois (arrependimento 7);
    # o item 1 vale 12 nas duas posições (arrependimento 0). A gulosa coloca
    # primeiro o 1 (maior valor); o arrependimento, primeiro o 0
    itens = [Item(3, 10), Item(2, 9), Item(3, 3)]
    assert ordem.insercao_gulosa([2], itens, 5) == [0, 1, 2]
    assert ordem.insercao_arrependimento([2], itens, 5) == [1, 0, 2]
