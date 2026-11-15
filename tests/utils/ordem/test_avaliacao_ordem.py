from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item

PESOS = [4, 3, 7, 5, 3, 2, 3]
VALORES = [12, 8, 17, 11, 6, 2, 2]
ITENS = [Item(p, v) for p, v in zip(PESOS, VALORES)]


def test_decodificar__insere_o_que_couber_na_ordem():
    solucao = [0, 1, 2, 3, 4, 5, 6]
    assert ordem.decodificar(solucao, ITENS, 9) == [1, 1, 0, 0, 0, 1, 0]
    assert ordem.avaliar(solucao, ITENS, 9) == 22


def test_decodificar__ordens_diferentes_mesma_solucao():
    # redundância da representação por ordem: as duas dão os itens 1 e 4
    primeira = ordem.decodificar([0, 3, 1, 2, 4, 5, 6], ITENS, 9)
    segunda = ordem.decodificar([3, 0, 6, 5, 4, 2, 1], ITENS, 9)
    assert primeira == segunda == [1, 0, 0, 1, 0, 0, 0]
    assert ordem.avaliar([3, 0, 6, 5, 4, 2, 1], ITENS, 9) == 23
