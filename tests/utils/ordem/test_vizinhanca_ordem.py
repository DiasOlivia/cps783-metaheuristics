from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item

ITENS = [Item(4, 12), Item(3, 8), Item(7, 17), Item(5, 11)]


def test_vizinhanca_troca__todas_as_trocas_com_os_itens_trocados():
    solucao = [2, 0, 3, 1]
    vizinhas = ordem.vizinhanca_troca(solucao, ITENS, 9)
    assert len(vizinhas) == 4 * 3 // 2
    # posições 1 e 3 trocam os itens 2 e 3
    assert vizinhas[1] == ("1↔3", (2, 3), [3, 0, 2, 1])
    assert all(sorted(vizinha) == [0, 1, 2, 3] for _, _, vizinha in vizinhas)
    assert solucao == [2, 0, 3, 1]
