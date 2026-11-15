import random

from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def _instancia():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def test_construtiva_aleatoria__permutacao():
    itens, capacidade = _instancia()
    assert sorted(ordem.construtiva_aleatoria(itens, capacidade)) == list(range(20))


def test_construtiva_gulosa__decodifica_na_solucao_gulosa():
    itens, capacidade = _instancia()
    solucao = ordem.construtiva_gulosa(itens, capacidade)
    gulosa = binaria.construtiva_gulosa(itens, capacidade)
    assert ordem.decodificar(solucao, itens, capacidade) == gulosa


def test_construtiva_gulosa_aleatoria__decodifica_na_mesma_solucao_da_binaria():
    itens, capacidade = _instancia()
    random.seed(7)
    solucao = ordem.construtiva_gulosa_aleatoria(itens, capacidade, alfa=0.5)
    random.seed(7)
    esperada = binaria.construtiva_gulosa_aleatoria(itens, capacidade, alfa=0.5)
    assert sorted(solucao) == list(range(20))
    assert ordem.decodificar(solucao, itens, capacidade) == esperada
