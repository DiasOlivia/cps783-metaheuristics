import random

from matplotlib.figure import Figure

from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.plot import plotar_comparacao
from metaheuristics.utils.plot import plotar_historico


def _historico_sa():
    random.seed(0)
    itens = gerar_instancia_aleatoria(10, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    _, historico = simulated_annealing_mochila(itens, capacidade, 50, 1, 0.5, 5)
    return historico


def test_plotar_historico__painel_extra_da_temperatura():
    figura = plotar_historico(_historico_sa(), valor_otimo=500, eixo_x="iteracao")
    assert isinstance(figura, Figure)
    assert len(figura.axes) == 2


def test_plotar_comparacao__uma_linha_por_rotulo():
    historico = _historico_sa()
    figura = plotar_comparacao({"A": historico, "B": historico})
    assert len(figura.axes[0].get_lines()) == 2
