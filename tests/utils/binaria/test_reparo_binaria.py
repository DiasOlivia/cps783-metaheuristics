import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item

# densidades 3, 2,67, 2,43, 2,2, 2, 1 e 0,67 (exemplo do README do guloso, C = 9)
ITENS = [Item(p, v) for p, v in zip([4, 3, 7, 5, 3, 2, 3], [12, 8, 17, 11, 6, 2, 2])]


def test_reparar__tira_os_de_pior_densidade_e_completa():
    solucao = [0, 1, 1, 0, 0, 1, 1]  # peso 15
    reparada = binaria.reparar(solucao, ITENS, 9)
    # saem o 6 (0,67), o 5 (1) e o 2 (2,43); depois entram o 0 (3) e o 5 de volta
    assert reparada == [1, 1, 0, 0, 0, 1, 0]
    assert solucao == [0, 1, 1, 0, 0, 1, 1]


def test_reparar__viavel_so_e_completada():
    assert binaria.reparar([0, 0, 0, 0, 0, 0, 0], ITENS, 9) == [1, 1, 0, 0, 0, 1, 0]
    cheia = [1, 1, 0, 0, 0, 1, 0]
    assert binaria.reparar(cheia, ITENS, 9) == cheia


def test_reparar__recusa_solucao_nao_binaria():
    with pytest.raises(ValueError):
        binaria.reparar([3, 0, 2, 1, 4, 5, 6], ITENS, 9)
