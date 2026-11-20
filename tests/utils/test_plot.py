import random
from itertools import pairwise

import numpy as np
from matplotlib.figure import Figure

from metaheuristics.estudo.adaptive_large_neighborhood_search import (
    adaptive_large_neighborhood_search_mochila,
)
from metaheuristics.estudo.simulated_annealing import simulated_annealing_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.plot import milhar
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


def test_plotar_historico__pesos_da_alns_no_painel_de_extras():
    random.seed(0)
    itens = gerar_instancia_aleatoria(10, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    _, historico = adaptive_large_neighborhood_search_mochila(
        itens, capacidade, 50, 1, 0.9, tamanho_segmento=10
    )
    figura = plotar_historico(historico)
    # valores, pesos e o eixo da direita, da temperatura
    assert len(figura.axes) == 3
    legenda = [texto.get_text() for texto in figura.axes[1].get_legend().get_texts()]
    assert legenda == [
        "remocao_aleatoria",
        "remocao_pior",
        "remocao_shaw",
        "insercao_aleatoria",
        "insercao_gulosa",
    ]
    assert figura.axes[2].get_ylabel() == "temperatura"


def test_plotar_historico__rotulos_dos_eixos():
    historico = _historico_sa()
    padrao = plotar_historico(historico, eixo_x="iteracao")
    assert padrao.axes[0].get_ylabel() == "valor"
    assert padrao.axes[1].get_xlabel() == "iteração"

    figura = plotar_historico(historico, rotulo_x="passo", rotulo_y="custo")
    assert figura.axes[0].get_ylabel() == "custo"
    assert figura.axes[1].get_xlabel() == "passo"


def test_plotar_historico__ponto_em_cada_nova_melhor():
    historico = _historico_sa()
    melhores = [
        historico["melhor_valor"][t] for t in sorted(historico["melhor_valor"])
    ]
    mudancas = 1 + sum(a != b for a, b in pairwise(melhores))

    figura = plotar_historico(historico)
    pontos = figura.axes[0].collections[0]
    assert len(np.asarray(pontos.get_offsets())) == mudancas
    assert pontos.get_label() == "nova melhor solução"


def test_milhar__separador_brasileiro():
    assert milhar(30289) == "30.289"
    assert milhar(500) == "500"
    assert milhar(1234.5) == "1.234,5"


def test_plotar_comparacao__uma_linha_por_rotulo():
    historico = _historico_sa()
    figura = plotar_comparacao({"A": historico, "B": historico})
    assert len(figura.axes[0].get_lines()) == 2
