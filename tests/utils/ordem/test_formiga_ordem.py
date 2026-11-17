import random

from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.feromonio import Feromonio
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria

# exemplo do README do guloso, C = 9
ITENS = [Item(p, v) for p, v in zip([4, 3, 7, 5, 3, 2, 3], [12, 8, 17, 11, 6, 2, 2])]


def test_construtiva_formiga__permutacao_que_decodifica_a_sequencia():
    random.seed(0)
    itens = gerar_instancia_aleatoria(15, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    for _ in range(20):
        ordem_formiga = ordem.construtiva_formiga(itens, capacidade)
        dentro = ordem.decodificar(ordem_formiga, itens, capacidade)
        quantos = sum(dentro)
        assert sorted(ordem_formiga) == list(range(15))
        # os itens escolhidos vêm primeiro, e o decodificador coloca exatamente eles
        assert all(dentro[j] for j in ordem_formiga[:quantos])


def test_construtiva_formiga__q0_1_comeca_pela_gulosa():
    gulosa = ordem.construtiva_formiga(ITENS, 9, q0=1)
    assert ordem.decodificar(gulosa, ITENS, 9) == binaria.construtiva_gulosa(
        ITENS, 9
    )


def test_construtiva_formiga__feromonio_na_transicao():
    # τ alto em (None, 6) e (6, 5): a formiga começa por 6 e vai para 5
    feromonio = Feromonio(1.0)
    feromonio[(None, 6)] = feromonio[(6, 5)] = 1e9
    random.seed(0)
    assert ordem.construtiva_formiga(ITENS, 9, feromonio)[:2] == [6, 5]


def test_trilha__transicoes_entre_os_itens_colocados():
    # a ordem tenta 3 (5), 0 (4) e 2 (não cabe); o caminho é None → 3 → 0
    assert ordem.trilha([3, 2, 0, 1, 4, 5, 6], ITENS, 9) == [(None, 3), (3, 0)]
