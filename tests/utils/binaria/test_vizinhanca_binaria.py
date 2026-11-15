from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item

ITENS = [Item(4, 2), Item(5, 2), Item(7, 3), Item(9, 4), Item(6, 4)]


def test_vizinhanca_flip__um_bit_por_item_inclusive_inviaveis():
    solucao = [0, 1, 0, 1, 1]
    vizinhas = binaria.vizinhanca_flip(solucao, ITENS, 23)
    assert [rotulo for rotulo, _, _ in vizinhas] == ["+1", "−2", "+3", "−4", "−5"]
    assert [alterados for _, alterados, _ in vizinhas] == [(i,) for i in range(5)]
    # (11011) passa da capacidade e continua na vizinhança
    assert vizinhas[0][2] == [1, 1, 0, 1, 1]
    assert solucao == [0, 1, 0, 1, 1]


def test_vizinhanca_flip_troca__flips_e_depois_trocas():
    vizinhas = binaria.vizinhanca_flip_troca([0, 1, 0, 1, 0], ITENS, 23)
    # 5 flips + 2 itens dentro × 3 fora
    assert len(vizinhas) == 5 + 2 * 3
    assert vizinhas[5] == ("2→1", (1, 0), [1, 0, 0, 1, 0])
