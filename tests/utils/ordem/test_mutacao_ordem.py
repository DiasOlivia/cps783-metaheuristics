import random

from metaheuristics.utils import ordem


def _sem(lista, item):
    return [i for i in lista if i != item]


def test_mutacao_insercao__move_um_item_de_lugar():
    random.seed(0)
    solucao = list(range(9))
    for _ in range(30):
        nova = ordem.mutacao_insercao(solucao, [], 0)
        # sem o item que mudou de lugar, a ordem dos outros é a mesma
        assert any(_sem(nova, item) == _sem(solucao, item) for item in solucao)
    assert solucao == list(range(9))


def test_mutacao_inversao__inverte_um_trecho():
    random.seed(0)
    solucao = list(range(9))
    for _ in range(30):
        nova = ordem.mutacao_inversao(solucao, [], 0)
        diferentes = [p for p in range(9) if nova[p] != solucao[p]]
        if diferentes:
            i, j = diferentes[0], diferentes[-1] + 1
            assert nova[i:j] == solucao[i:j][::-1]
    assert solucao == list(range(9))


def test_mutacao__k_aplicacoes_continuam_permutacao():
    random.seed(1)
    for mutacao in (ordem.mutacao_insercao, ordem.mutacao_inversao):
        assert sorted(mutacao(list(range(10)), [], 0, k=5)) == list(range(10))
